"""
pyodide-mkdocs-theme
Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""
# pylint: disable=multiple-statements, attribute-defined-outside-init, unused-argument





import json
from textwrap import dedent
from typing import Any, Dict, List, Set, Tuple, Type, Optional, Union, TYPE_CHECKING
from itertools import starmap
from dataclasses import dataclass
from math import inf
from collections import defaultdict
from pathlib import Path


from mkdocs.exceptions import BuildError
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.plugins import event_priority


from .. import html_builder as Html
from ..tools_and_constants import (
    INSERTIONS_KINDS,
    MERMAID_CODE,
    IdeConstants,
    Kinds,
    PageUrl,
    EditorName,
    ScriptKind,
)
from ..parsing import eat, compress_LZW
from ..paths_utils import PathOrStr
from ..pyodide_logger import logger
from ..scripts_templates import SCRIPTS_TEMPLATES

from .maestro_tools import AutoCounter
from .maestro_meta import MaestroMeta
from .maestro_indent import MaestroIndent


if TYPE_CHECKING:
    from .pyodide_macros_plugin import PyodideMacrosPlugin








class MaestroIDE(MaestroIndent):
    """ Holds the global logic related to the IDE macros """


    generic_count: int = AutoCounter()
    """
    Number of empty terminals (per site count. Related to the terminal() macro).
    Since there are no data associated to these in the locale storage (at least, no _important_
    data), this counter is used for everything.
    """

    ide_count: int = AutoCounter()
    """
    Number of empty IDEs (per site count. Used for IDE without python files).
    Dedicated counter, for legacy reasons. Might break users' storage sometimes, but this will
    provide more consistency with the evolution of the redactor's documentation.
    """

    _editors_ids:  Set[str]
    """
    Store the ids of all the created IDEs, to enforce their uniqueness.
    """

    _scripts_or_link_tags_to_insert: Dict[ScriptKind,str]
    """
    UI formatting scripts to insert only in pages containing IDEs or terminals.
    Note that the values are all the scripts and/or css tags needed for the key kind,
    all joined together already, as a template string expecting the variable `to_base`.

    Defined once, through a call to register_js_and_css_tags at star building time.
    """

    _pages_configs: Dict[PageUrl, 'PageConfiguration']
    """
    Represent the configurations of every IDE in every Page of the documentation.
    """

    _pages_with_mermaid: Set[PageUrl]
    """
    Keeps track of the pages the already contains the injected mermaid hidden graph.
    (this avoids to insert it a lot of times while once is enough)
    """

    def on_config(self, config:MkDocsConfig):

        self.generic_count = 0
        self.ide_count = 0
        self._editors_ids = set()
        self._pages_configs = defaultdict(lambda: PageConfiguration(self))
        self._scripts_or_link_tags_to_insert = {}
        self._pages_with_mermaid = set()

        self.register_js_and_css_tags(SCRIPTS_TEMPLATES)

        super().on_config(config)   # pylint: disable=no-member



    @MaestroMeta.meta_config_swap
    def on_page_markdown(
        self,
        markdown:str,
        page:Page,
        config:MkDocsConfig,
        site_navigation=None,
        **kwargs
    ):
        markdown_out = super().on_page_markdown(
            markdown, page, config, site_navigation=site_navigation, **kwargs
        )
        if self.does_current_page_need(Kinds.mermaid):
            markdown_out += MERMAID_CODE

        return markdown_out


    @MaestroMeta.meta_config_swap
    @event_priority(2000)
    def on_page_context(self,_ctx, page:Page, *, config:MkDocsConfig, nav:Navigation):
        """
        Spot pages in which corrections and remarks have been inserted, and encrypt them.

        This hook uses high priority because the html content must be modified before the search
        plugin starts indexing stuff in it (which precisely happens in the on_page_context hook).
        """
        # pylint: disable=pointless-string-statement

        if self.is_page_with_something_to_insert(page):
            logger.debug(f"Add scripts + encrypt solutions and remarks in { self.file_location() }")

            chunks = []
            self.chunk_and_encrypt_solutions_and_rems(page.content, chunks)
            self.add_css_or_js_scripts(page, chunks)
            page.content = ''.join(chunks)


        if hasattr(super(), 'on_page_context'):
            super().on_page_context(_ctx, page, config=config, nav=nav)



    # ---------------------------------------------------------------------------------



    def register_if_unique(self, id_ide:str):
        """
        Check if the given id has already been used.
        If so, return False. If not, register it and return True.
        """
        if id_ide in self._editors_ids:
            return False
        self._editors_ids.add(id_ide)
        return True



    def get_hdr_and_public_contents_from(
        self, opt_path_or_content: Union[ Optional[Path], str ],
    ) -> Tuple[str,str,str]:
        """
        Extract the header code and the public content from the given file (assuming it's a
        python file or possibly None, if @path is coming from get_sibling_of_current_page).

        @returns: (header, user_content, public_tests) where header and content may be an
                  empty string.
        """
        if isinstance(opt_path_or_content,str):
            content = opt_path_or_content
        else:
            if opt_path_or_content is None or not opt_path_or_content.is_file():
                return '','',''
            content = opt_path_or_content.read_text(encoding="utf-8")

        lst = IdeConstants.hdr_pattern.split(content)
        # NOTE: If HDR tokens are present, split will return an empty string as first element, so:
        #   - len == 1 : [content]
        #   - len == 3 : ['', hdr, content]

        if len(lst) not in (1,3):
            raise BuildError(
                f"Wrong number of HDR/ENV tokens (found { len(lst)-1 }) in:\n"
                f"{opt_path_or_content!s}"
            )

        hdr = "" if len(lst)==1 else lst[1]
        content = lst[-1].strip()
        tests_cuts = self.lang.tests.as_pattern.split(content)
        if len(tests_cuts)>2:
            pattern = self.lang.tests.as_pattern.pattern
            raise BuildError(
                f'Found more than one time the token { pattern } (case insensitive) in:\n'
                + opt_path_or_content
            )
        user_code, public_tests, *_ = map(str.strip, tests_cuts + [''])
        return hdr, user_code, public_tests



    def get_sibling_of_current_page(
        self, partial_path: PathOrStr, *, tail:str="", rel_to_docs:bool=False
    ):
        """
        @env: BaseMaestro
        @docs_dir
        Extract the current page from the env, then build a path name toward a file using
        the @partial_path (string name of slash separated string, or relative Path), starting
        from the same parent directory.
        If @tail is given, it is added to the name of the last segment of of the built path.
        If @rel_to_docs is False, the result will be an absolute path of the file at documentation
        building time. If @rel_to_docs is True, the returned path will be rooted at the docs_dir,
        meaning the path will also be the valid relative path of the file on the built site.

        If @partial_path is an empty string or a Path without name, return None
        """
        path: Path = self.docs_dir_path / self.page.file.src_uri
        out_path = self._get_sibling(path, partial_path, tail)
        if out_path and rel_to_docs:
            return out_path.relative_to(self.docs_dir_path)
        return out_path


    @staticmethod
    def _get_sibling(src:Path, rel:PathOrStr, tail:str="") -> Optional[Path] :
        """ Build a sibling of the given path file, replacing the current Path.name
            with the given @rel element (path or str).
            If @tail is given, it is added to the name of the built path.
            Return None if:
                - @src has no explicit parent (using '.' on the cwd will cause troubles)
                - @rel is an empty string or is a Path without name property (empty IDE)
        """
        if not src.name or not rel or isinstance(rel,Path) and not rel.name:
            return None

        possible_paths = [
            src.parent / rel,
            src.parent / 'scripts' / src.stem / rel
        ]
        for path in possible_paths:
            if tail:
                path = path.with_name( path.stem + tail )
            if path.is_file():
                return path

        return None



    #-----------------------------------------------------------------------
    #     Manage scripts and css to include only in some specific pages
    #-----------------------------------------------------------------------



    def register_js_and_css_tags(self, scripts_dct:Dict[ScriptKind,str]):
        """
        Done once only.
        Store and adapt the html code needed to load scripts or styles directly from the page
        content. Those will be inserted at the end of a document, but still inside the its body.
        """
        kinds_diff = set(scripts_dct) - INSERTIONS_KINDS
        assert not kinds_diff, "Unknown kind(s) of scripts: " + ', '.join(kinds_diff)

        self._scripts_or_link_tags_to_insert = {
            kind: script.replace(
                '{{ config.plugins.pyodide_macros.rebase(base_url) }}',
                "{to_base}"
            )
            for kind,script in scripts_dct.items()
        }

        logger.info("Registered js and css to insert in specific pages")
        logger.info("".join(
            f'\n{kind: >10}: ' + s.strip().replace('\n', '\n'.ljust(13))
            for kind,s in self._scripts_or_link_tags_to_insert.items()
        ))


    #---------------------------------------------------------------------------------------


    def set_current_page_js_data(self, editor_name:str, prop:str, data:Union[str,int]):
        """
        Store data for an IDE in the current Page. @prop must be a property of the IdeConfig class.
        """
        self._pages_configs[self.page.url].set(editor_name, prop, data)


    def set_current_page_insertion_needs(self, *kind:ScriptKind):
        """ Mark a page url as needing some specific kinds of scripts (depending on the macro
            triggering the call). """
        self._pages_configs[self.page.url].needs.update(kind)


    def does_current_page_need(self, kind:ScriptKind):
        return kind in self._pages_configs[self.page.url].needs



    def is_page_with_something_to_insert(self, page:Optional[Page]=None):
        """
        Check if the current page is marked as holding at least one thing needing a script,
        insertion or ide content.
        If @page is given, use this instance instead of the one from self.page (useful for hooks)
        """
        url = page.url if page else self.page.url
        return url in self._pages_configs


    def add_css_or_js_scripts(self, page:Page, chunks:List[str]):
        """
        Build the string needed to insert the page specific formatting scripts in the
        page that will land at the given url, updating the path to reach the location
        of the scripts in the custom_dir.

        NOTE: assumption is made that, if this method is called, it's been already
              checked that there there actually _are_ scripts to insert for this page
              (see __init__:on_post_page_macros)
        """
        page = page or self.page
        url = page.url
        going_up = self.level_up_from_current_page(url)
        page_config = self._pages_configs[url]
        page_config.dump_as_scripts(going_up, self._scripts_or_link_tags_to_insert, chunks)







    #--------------------------------------------------------------------
    #                    Solution & remarks encryption
    #--------------------------------------------------------------------



    def chunk_and_encrypt_solutions_and_rems(self, html:str, chunks:List[str]):
        """
        Assuming it's known that the @page holds corrections and/or remarks:
            - Search for the encryption tokens
            - Encrypt the content in between two consecutive tokens in the page html content.
            - Once done for the whole page, replace the page content with the updated version.
        Encryption tokens are removed on the way.
        """
        if not self.encrypt_corrections_and_rems:
            chunks.append(html)
            return

        entering = 0
        while entering < len(html):
            i,j = eat(html, IdeConstants.encryption_token, start=entering, skip_error=True)
            i,j = self._cleanup_p_tags_around_encryption_tokens(html, i, j)

            chunks.append( html[entering:i] )

            if i==len(html):
                break

            ii,entering = eat(html, IdeConstants.encryption_token, start=j)     # raise if not found
            ii,entering = self._cleanup_p_tags_around_encryption_tokens(html, ii, entering)

            solution_and_rem = html[j:ii].strip()
            encrypted_content = compress_LZW(solution_and_rem, self)
            chunks.append(encrypted_content)



    def _cleanup_p_tags_around_encryption_tokens(self, html:str, i:int, j:int):
        """
        mkdocs automatically surrounds the encryption token with <p> tag, so they must be removed.
        Note: Including the tags in the ENCRYPTION_TOKEN doesn't change the problem: you'd just
              get another <p> tag surrounding the token... sometimes... x/
        """
        while html[i-3:i]=='<p>' and html[j:j+4]=='</p>':
            i-=3 ; j+=4
        return i,j


















MAYBE_LISTS: Tuple[str,...] = ('excluded', 'excluded_methods', 'white_list', 'python_libs')


@dataclass
class IdeConfig:
    """
    Configuration of one IDE in one page of the documentation. Convertible to JS, to define the
    global variable specific to each page.

    Always instantiated without arguments, and items are updated when needed.
    """

    py_name:      str = ""          # name to use for downloaded file
    env_content:  str = ""          # HDR part of "exo.py"
    env_term_content:  str = ""     # HDR part for terminal commands only
    user_content: str = ""          # Non-HDR part of "exo.py" (initial code)
    corr_content: str = ""          # not exported to JS!
    public_tests: str = ""          # test part of "exo.py" (initial code)
    secret_tests: str = ""          # Content of "exo_test.py" (private tests)
    post_term_content: str = ""     # Content to run after for terminal commands only
    post_content: str = ""          # Content to run after executions are done

    excluded: List[str] = None      # List of forbidden instructions (functions or packages)
    excluded_methods: List[str] = None # List of forbidden methods accesses
    rec_limit: int = None           # recursion depth to use at runtime, if defined (-1 otherwise).
    white_list: List[str] = None    # White list of packages to preload at runtime

    profile: str = None
    attempts_left: int = None       # Not overwriting this means there is no counter displayed
    auto_log_assert: bool = None    # Build automatically missing assertion messages during validations
    corr_rems_mask: int = None      # Bit mask:   has_corr=corr_rems_mask&1 ; has_rem=corr_rems_mask&2
    has_check_btn: bool = None      # Store the info about the Ide having its check button visible or not
    is_encrypted: bool = None       # Tells if the sol & REMs div content is encrypted or not
    is_vert: bool = None            # IDEv if true, IDE otherwise.
    max_ide_lines: int = None       # Max number of lines for the ACE editor div
    decrease_attempts_on_code_error: bool = None    # when errors before entering the actual validation
    deactivate_stdout_for_secrets: bool = None
    show_only_assertion_errors_for_secrets: bool = None
    python_libs: List[str] = None

    prefill_term: str = None        # Command to insert in the terminal after it's startup.
    stdout_cut_off: int = None      # max number of lines displayed at once in a jQuery terminal



    def dump_to_js_code(self):
        """
        Convert the current config to a valid string representation of a JS object.
        """
        content = ', '.join(
            f'"{k}": { typ }'                  # pylint: disable-next=no-member
            for k,typ in starmap(self._convert, self.__class__.__annotations__.items())
            if typ is not None      # This filtering operation
        )
        return f"{ '{' }{ content }{ '}' }"



    def _convert(self, prop:str, typ:Type):
        """
        Convert the current python value to the equivalent "code representation" for a JS file.
        @prop: property name to convert
        @typ: type (annotation) of the property
        @returns: str
        """
        val = getattr(self, prop)
        if val is None:
            return prop, None

        is_lst = prop in MAYBE_LISTS
        if is_lst:           return prop, json.dumps(val or [])
        if val == inf:       return prop, '"Infinity"'
        if typ is bool:      return prop, str(val).lower() if val is not None else "null"
        if typ in (int,str): return prop, json.dumps(val)

        raise NotImplementedError(
            f"Conversion for {prop}:{typ} in {self.__class__.__name__} is not implemented"
        )













class PageConfiguration(Dict[EditorName,IdeConfig]):
    """
    Represent the Configuration for one single page of the documentation (when needed).
    Holds the individual configurations for each IDE in the page, and also the set registering
    the different kinds of ScriptKind that the page will need to work properly.

    The purpose of this kind of object is to be dumped as html later.
    """

    def __init__(self, env):
        super().__init__()
        self.env: PyodideMacrosPlugin = env
        self.needs: Set[ScriptKind] = set()



    def set(self, editor_name:str, prop:str, value:Any):
        """ Register an IDE configuration property, creating the IdeConfig on the fly,
            if it doesn't exist yet.
        """
        if self.env._dev_mode and prop not in IdeConfig.__annotations__:    # pylint: disable=no-member, protected-access
            msg = f'{prop!r} is not a valide attribut of { IdeConfig.__name__ } class'
            raise AttributeError(msg)

        if editor_name not in self:
            self[editor_name] = IdeConfig()

        setattr(self[editor_name], prop, value)



    def dump_as_scripts(self,
            going_up:str,
            kind_to_scripts:Dict[ScriptKind,str],
            chunks:List[str],
        ):
        """
        Create the <script> tag containing the "global" object to define for all the IDEs in the
        current page, and yield it with all the scripts or css contents to insert in that page.

        @going_up:          Relative path string allowing to retrieve the root level of the docs.
        @kind_to_scripts:   Relations between kinds and the scripts the involve.
        @chunks:            List of slices of the current page. The insertions must be added to it.
        """

        # Yield the global variable first, because the JS scripts will use it at runtime:

        encoded = global_var = '{' + ', '.join(
            f'"{ editor_name }": { conf.dump_to_js_code() }' for editor_name,conf in self.items()
        )+'}'

        # print(json.loads(global_var))     # To check the validity of the dumped data
        # print(repr(global_var))

        if self.env.encrypted_js_data:
            encoded = compress_LZW(global_var, self.env)


        need_mermaid = Kinds.mermaid in self.needs
        chunks.append(Html.script(dedent(
            f"""
            CONFIG.needMermaid = { json.dumps(need_mermaid) };
            let PAGE_IDES_CONFIG = { encoded !r}
            """
        )))
        self.needs.discard(Kinds.mermaid)

        # Spot invalid kinds:
        missed = {kind for kind in self.needs if kind.name not in kind_to_scripts}
        if missed:
            logger.error(
                "Some macros are registering the need for these kinds while there are no files "
              + "registered for them:"
              + ''.join(f"\n    { ScriptKind.__name__ }.{ k }" for k in missed)
            )

        # Then register all the scripts and/or css the current page is needing:
        for kind in sorted(self.needs):
            insertion = kind_to_scripts[kind.name].format(to_base=going_up)
            chunks.append(insertion)
