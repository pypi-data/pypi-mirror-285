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
# pylint: disable=multiple-statements


from functools import wraps
import re
import json
from typing import  List, Optional
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import BuildError
from mkdocs.structure.pages import Page
from mkdocs.plugins import BasePlugin

from ...__version__ import __version__
from ..tools_and_constants import ICONS_IN_TEMPLATES_DIR
from ..exceptions import PyodideMacrosDeprecationError, PyodideMacrosError
from ..messages import Lang
from ..pyodide_logger import logger
from .maestro_tools import ConfigExtractor, dump_and_dumper
from .config import PyodideMacrosConfig






TO_DUMP_TO_CONFIG = """
    args_figure_div_id
    base_url
    button_icons_directory
    cut_feedback
    pmt_url
    python_libs
    in_serve
    version
""".split()





class BaseMaestro(BasePlugin[PyodideMacrosConfig]):
    """
    Main class, regrouping the basic configurations, properties, getters and/or constants
    for the different children classes: each of them will inherit from MaestroConfig.
    It is also used as "sink" for the super calls of other classes that are not implemented
    on the MacrosPlugin class.

    Note that, for the ConfigExtractor for to properly work, the class hierarchy has to
    extend MacrosPlugin at some point.
    """

    encrypted_js_data:                  bool = ConfigExtractor('build')
    ignore_macros_plugin_diffs:         bool = ConfigExtractor('build')
    forbid_macros_override:             bool = ConfigExtractor('build')
    skip_py_md_paths_names_validation:  bool = ConfigExtractor('build')
    load_yaml_encoding:                 str  = ConfigExtractor('build')
    meta_yaml_encoding:                 str  = ConfigExtractor('build')
    macros_with_indents:           List[str] = ConfigExtractor('build')
    tab_to_spaces:                      int  = ConfigExtractor('build')
    python_libs:                   List[str] = ConfigExtractor('build')
    _pmt_meta_filename:                 str  = ConfigExtractor('build')
    deprecation_level:                  str  = ConfigExtractor('build')

    decrease_attempts_on_user_code_failure:           bool = ConfigExtractor("ides")
    deactivate_stdout_for_secrets:          Optional[bool] = ConfigExtractor("ides")
    encrypt_alpha_mode:                                str = ConfigExtractor("ides")
    encrypt_corrections_and_rems:                     bool = ConfigExtractor('ides')
    forbid_secrets_without_corr_or_REMs:              bool = ConfigExtractor('ides')
    forbid_hidden_corr_and_REMs_without_secrets:      bool = ConfigExtractor('ides')
    forbid_corr_and_REMs_with_infinite_attempts:      bool = ConfigExtractor('ides')
    show_only_assertion_errors_for_secrets: Optional[bool] = ConfigExtractor("ides")

    stdout_cut_off: int = ConfigExtractor("terms")
    cut_feedback:   int = ConfigExtractor("terms")

    forbid_no_correct_answers_with_multi: bool = ConfigExtractor('qcms')


    # global mkdocs config data:
    docs_dir:    str = ConfigExtractor(root='_conf')
    repo_url:    str = ConfigExtractor(root='_conf')
    site_name:   str = ConfigExtractor(root='_conf')
    site_url:    str = ConfigExtractor(root='_conf')
    site_dir:    str = ConfigExtractor(root='_conf')

    # Specific to the original macros plugin:
    _dev_mode:               bool = ConfigExtractor()
    j2_block_start_string:    str = ConfigExtractor()
    j2_block_end_string:      str = ConfigExtractor()
    j2_variable_start_string: str = ConfigExtractor()
    j2_variable_end_string:   str = ConfigExtractor()


    # ARGS EXTRACTOR TOKEN
    args_IDE_py_name: str = ConfigExtractor('args.IDE', prop='py_name')
    args_IDE_SANS: str = ConfigExtractor('args.IDE', prop='SANS')
    args_IDE_WHITE: str = ConfigExtractor('args.IDE', prop='WHITE')
    args_IDE_REC_LIMIT: int = ConfigExtractor('args.IDE', prop='REC_LIMIT')
    args_IDE_MERMAID: bool = ConfigExtractor('args.IDE', prop='MERMAID')
    args_IDE_MAX: int = ConfigExtractor('args.IDE', prop='MAX')
    args_IDE_LOGS: bool = ConfigExtractor('args.IDE', prop='LOGS')
    args_IDE_MAX_SIZE: int = ConfigExtractor('args.IDE', prop='MAX_SIZE')
    args_IDE_TERM_H: int = ConfigExtractor('args.IDE', prop='TERM_H')
    args_IDE_MODE: str = ConfigExtractor('args.IDE', prop='MODE')
    args_terminal_py_name: str = ConfigExtractor('args.terminal', prop='py_name')
    args_terminal_SANS: str = ConfigExtractor('args.terminal', prop='SANS')
    args_terminal_WHITE: str = ConfigExtractor('args.terminal', prop='WHITE')
    args_terminal_REC_LIMIT: int = ConfigExtractor('args.terminal', prop='REC_LIMIT')
    args_terminal_MERMAID: bool = ConfigExtractor('args.terminal', prop='MERMAID')
    args_terminal_TERM_H: int = ConfigExtractor('args.terminal', prop='TERM_H')
    args_terminal_FILL: str = ConfigExtractor('args.terminal', prop='FILL')
    args_py_btn_py_name: str = ConfigExtractor('args.py_btn', prop='py_name')
    args_py_btn_SANS: str = ConfigExtractor('args.py_btn', prop='SANS')
    args_py_btn_WHITE: str = ConfigExtractor('args.py_btn', prop='WHITE')
    args_py_btn_REC_LIMIT: int = ConfigExtractor('args.py_btn', prop='REC_LIMIT')
    args_py_btn_MERMAID: bool = ConfigExtractor('args.py_btn', prop='MERMAID')
    args_py_btn_WRAPPER: str = ConfigExtractor('args.py_btn', prop='WRAPPER')
    args_py_btn_HEIGHT: int = ConfigExtractor('args.py_btn', prop='HEIGHT')
    args_py_btn_WIDTH: int = ConfigExtractor('args.py_btn', prop='WIDTH')
    args_py_btn_SIZE: int = ConfigExtractor('args.py_btn', prop='SIZE')
    args_py_btn_ICON: str = ConfigExtractor('args.py_btn', prop='ICON')
    args_py_btn_TIP: str = ConfigExtractor('args.py_btn', prop='TIP')
    args_py_btn_TIP_SHIFT: int = ConfigExtractor('args.py_btn', prop='TIP_SHIFT')
    args_py_btn_TIP_WIDTH: float = ConfigExtractor('args.py_btn', prop='TIP_WIDTH')
    args_section_py_name: str = ConfigExtractor('args.section', prop='py_name')
    args_section_section: str = ConfigExtractor('args.section', prop='section')
    args_multi_qcm_description: str = ConfigExtractor('args.multi_qcm', prop='description')
    args_multi_qcm_hide: bool = ConfigExtractor('args.multi_qcm', prop='hide')
    args_multi_qcm_multi: bool = ConfigExtractor('args.multi_qcm', prop='multi')
    args_multi_qcm_shuffle: bool = ConfigExtractor('args.multi_qcm', prop='shuffle')
    args_multi_qcm_shuffle_questions: bool = ConfigExtractor('args.multi_qcm', prop='shuffle_questions')
    args_multi_qcm_shuffle_items: bool = ConfigExtractor('args.multi_qcm', prop='shuffle_items')
    args_multi_qcm_admo_kind: str = ConfigExtractor('args.multi_qcm', prop='admo_kind')
    args_multi_qcm_admo_class: str = ConfigExtractor('args.multi_qcm', prop='admo_class')
    args_multi_qcm_qcm_title: str = ConfigExtractor('args.multi_qcm', prop='qcm_title')
    args_multi_qcm_DEBUG: bool = ConfigExtractor('args.multi_qcm', prop='DEBUG')
    args_py_py_name: str = ConfigExtractor('args.py', prop='py_name')
    args_figure_div_id: str = ConfigExtractor('args.figure', prop='div_id')
    args_figure_div_class: str = ConfigExtractor('args.figure', prop='div_class')
    args_figure_inner_text: str = ConfigExtractor('args.figure', prop='inner_text')
    args_figure_admo_kind: str = ConfigExtractor('args.figure', prop='admo_kind')
    args_figure_admo_class: str = ConfigExtractor('args.figure', prop='admo_class')
    args_figure_admo_title: str = ConfigExtractor('args.figure', prop='admo_title')
    # ARGS EXTRACTOR TOKEN


    _encrypt_corrections_and_rems:                bool = ConfigExtractor("build", deprecated=True)
    _forbid_secrets_without_corr_or_REMs:         bool = ConfigExtractor('build', deprecated=True)
    _forbid_hidden_corr_and_REMs_without_secrets: bool = ConfigExtractor('build', deprecated=True)
    _forbid_corr_and_REMs_with_infinite_attempts: bool = ConfigExtractor('build', deprecated=True)
    _bypass_indent_errors:                        bool = ConfigExtractor('build', deprecated=True)
    _show_assertion_code_on_failed_test:          bool = ConfigExtractor('ides', deprecated=True)
    _max_attempts_before_corr_available:           int = ConfigExtractor('ides', deprecated=True)
    _default_ide_height_lines:                     int = ConfigExtractor('ides', deprecated=True)
    _default_height_ide_term:                      int = ConfigExtractor('terms', deprecated=True)
    _default_height_isolated_term:                 int = ConfigExtractor('terms', deprecated=True)
    _hide:                                        bool = ConfigExtractor('qcms', deprecated=True)
    _multi:                                       bool = ConfigExtractor('qcms', deprecated=True)
    _shuffle:                                     bool = ConfigExtractor('qcms', deprecated=True)
    _scripts_url:                                  str = ConfigExtractor("_others", deprecated=True)
    _site_root:                                    str = ConfigExtractor("_others", deprecated=True)



    #----------------------------------------------------------------------------
    # WARNING: the following properties are assigned from "other places":
    #   - pages from the original MacrosPlugin
    #   - others from PyodideMacrosPlugin

    page: Page  # just as a reminder: defined by MacrosPlugin

    docs_dir_path: Path
    """ Current docs_dir of the project as a Path object (ABSOLUTE path) """

    docs_dir_cwd_rel: Path
    """ docs_dir Path object, but relative to the CWD, at runtime """

    _macro_with_indent_pattern:re.Pattern = None
    """
    Pattern to re.match macro calls that will need to handle indentation levels.
    Built at runtime (depends on `macro_with_indents`)
    """

    #----------------------------------------------------------------------------
    # Transferred to JS CONFIG:

    base_url:str = ""
    button_icons_directory:str = ""
    pmt_url:str = 'https://gitlab.com/frederic-zinelli/pyodide-mkdocs-theme'
    version:str = __version__
    in_serve:bool = False
    lang:Lang = None





    # Override MacroPlugin
    def on_config(self, config:MkDocsConfig):       # pylint: disable=missing-function-docstring

        self.in_serve = config.dev_addr.host in config.site_url
        self.lang     = Lang()
        self.lang.register_env(self)

        if self.skip_py_md_paths_names_validation:
            logger.warning("The build.skip_py_md_paths_names_validation option is activated.")

        super().on_config(config)   # pylint: disable-next=no-member
                                    # MacrosPlugin is actually "next in line" and has the method


    # Override MacroPlugin
    def macro(self, func, name=""):     # pylint: disable=arguments-renamed
        """
        Add an extra wrapper around the macro, so that the different classes can inject
        their logic around the macros calls themselves, when needed.
        """

        # Raise if different macros are registered with the same name (unless allowed).
        # Note: the macro plugin creates a fresh dict on each on_config hook.
        name = name or func.__name__
        if self.forbid_macros_override and name in self.macros:
            raise PyodideMacrosError(
                f'A macro named "{name}" has already been registered, possibly by the theme '
                f'itself.\nPlease remove or rename the { name } macro is in the module: '
                f'{ func.__module__ }'
            )

        @wraps(func)
        def wrapper(*a,**kw):
            """ Delegate the macro execution to the instance method : allow each Maestro level to
                apply its own/dedicated logic, keeping everything perfectly self contained and
                consistent.
                (This is complex, but this is a beautiful piece of logic... XD )
            """
            return self.apply_macro(name, func, *a, **kw)

        wrapper.__name__ = wrapper.__qualname__ = name
        return super().macro(wrapper, name)


    def apply_macro(self, name, func, *a, **kw):            # pylint: disable=unused-argument
        """ Root method: just call the macro... """
        return func(*a, **kw)


    #----------------------------------------------------------------------------


    def file_location(self, page:Optional[Page]=None):
        """ Path to the current file, relative to the cwd. """
        page = page or getattr(self, 'page', None)
        if not page:
            raise BuildError("No page defined yet")
        return f"{ self.docs_dir_cwd_rel }/{ page.file.src_uri }"


    def level_up_from_current_page(self, url:str=None) -> str:
        """
        Return the appropriate number of ".." steps needed to build a relative url to go from the
        current page url back to the root directory.

        Note there are no trailing backslash.

        @url: relative to the docs_dir (ex: "exercices/ ..."). If None, use self.page.url instead.
        """
        url = self.page.url if url is None else url
        page_loc:Path = self.docs_dir_path / url
        segments = page_loc.relative_to(self.docs_dir_path).parts
        out = len(segments) * ['..']
        return '/'.join(out) or '.'


    #----------------------------------------------------------------------------


    def rebase(self, base_url:str):
        """
        Necessary for development only (to replace the wrong base_url value during a serve in the
        theme project)
        NOTE: Keep in mind the base_url SOMETIMES ends with a slash...
        """
        return base_url if base_url!='/' else '.'


    def dump_to_js_config(self, base_url):
        """
        Create the <script> tag that will add all the CONFIG properties needed in the JS
        global config file, and also applies the post conversion where needed.

        !!! WARNING !!!
            This method is called from the main.html template, so self.page HAS NO MEANING here!
        """

        # Don't declare to_dump as class var: won't be available when the method is called
        # with None instead of self... (see HACK just below).
        to_dump = TO_DUMP_TO_CONFIG

        # HACK!
        # This method can be called with self being None to build the placeholder CONFIG in
        # 0_config-libs.js, si fill the data only when self actually exists.
        if self:                                # pylint: disable=w0201
            if self._dev_mode:
                to_dump = to_dump + ['_dev_mode']       # DO NOT MUTATE!
            base_url = self.rebase(base_url).rstrip('/')
            self.button_icons_directory = f"{base_url}/{ICONS_IN_TEMPLATES_DIR}"
            self.base_url = base_url

            # This is ugly, but I need to convert the python_libs relative paths to names...:
            true_libs = self.python_libs[:]
            self.python_libs[:] = ( s.split('/')[-1] for s in true_libs )

        try:
            dct = dump_and_dumper(to_dump, self, json.dumps)
            dct['lang'] = Lang.dump_as_str(self and self.lang)
                # (the Lang dump requires a slightly different logic)

        finally:        # Make absolutely sure the original state of python_libs will be restored
            if self:
                self.python_libs[:] = true_libs

        if self:                        # HACK!

            # Dump to main.html, then adding post conversions operations:
            dumping = [ f"\n  CONFIG.{ prop } = { val }" for prop,val in dct.items() ]
            dumped = f'''\
<script type="application/javascript">
{ "".join(dumping) }

CONFIG.lang.tests.as_pattern = new RegExp(CONFIG.lang.tests.as_pattern, 'i')
CONFIG.pythonLibs = new Set(CONFIG.pythonLibs)
</script>'''


        else:
            # Dump the placeholders to the JS config-libs file:
            dumping = [ f"\n    { prop }: { val }," for prop,val in dct.items() ]
            dumped = ''.join(dumping)

        return dumped


    #----------------------------------------------------------------------------


    def _omg_they_killed_keanu(self,page_name:str, page_on_context:Page=None):
        """ Debugging purpose only. Use as breakpoint utility.
            @page_on_context argument used when called "outside" of the macro logic (fro example,
            in external hooks)
        """
        page = page_on_context or self.page
        if page_name == page.url:
            logger.error("Breakpoint! (the CALL to this method should be removed)")


    def warn_unmaintained(self, that:str=None, *, msg:str=None):
        """
        Generic warning message for people trying to used untested/unmaintained macros.
        """
        msg = msg or (
            f"{ that.capitalize() } has not been maintained since the original pyodide-mkdocs "
            "project, may not currently work, and will be removed in the future.\n"
            "Please open an issue on the pyodide-mkdocs-theme repository, if you need it.\n\n"
            f"\t{ self.pmt_url }.\n"
            "If you absolutely need to pass the build right now, you can change the plugin option "
            "build.deprecation_level to 'warn'."
        )
        if self.deprecation_level == 'error':
            raise PyodideMacrosDeprecationError(msg)
        else:
            logger.error(msg)
