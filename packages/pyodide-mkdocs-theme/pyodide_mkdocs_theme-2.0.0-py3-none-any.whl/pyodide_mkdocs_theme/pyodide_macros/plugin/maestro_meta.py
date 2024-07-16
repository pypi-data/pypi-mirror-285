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
from typing import Any, ClassVar, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from mkdocs.exceptions import BuildError
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page

from pyodide_mkdocs_theme.pyodide_macros.plugin.config.args_macros_config import ARGS_MACRO_CONFIG
from pyodide_mkdocs_theme.pyodide_macros.plugin.maestro_base import BaseMaestro



from ..exceptions import PyodideMacrosMetaError
from .config import PyodideMacrosConfig, CopyableConfig









class MaestroMeta(BaseMaestro):
    """ Handles the .meta.pmt.yml values and the meta sections in Pages. """

    __pmt_meta_wrapped__: str = "__pmt_meta_wrapped__"
    """
    Property added to the mkdocs events decorated with MaestroMeta.meta_config_swap. This property
    allows to enforce proper contracts on the config values, whatever the plugin inheritance chain.
    """

    _meta_tree: Optional['MetaTree'] = None
    """
    Tree holding all the meta configs, merging the data appropriately at any depth.
    """


    def on_config(self, config:MkDocsConfig):

        self.check_config_swap_decorations()

        super().on_config(config)

        # Then gather all the meta files
        self._meta_tree = MetaTree.create(self.config)

        for meta_path in self.docs_dir_path.rglob(self._pmt_meta_filename):

            content  = meta_path.read_text(encoding=self.meta_yaml_encoding)
            meta_dct = yaml.load(content, Loader=yaml.Loader)
            meta_rel = meta_path.relative_to(self.docs_dir_path)

            self._meta_tree.insert_meta_file(meta_dct, meta_rel, self.docs_dir_cwd_rel)



    def check_config_swap_decorations(self):
        """
        Check the top event calls in the hierarchy are wrapped with the MaestroMeta decorator.
        At the time of writing this class, the hierarchy leads to these qualified names:

            PyodideMacrosPlugin
            MaestroExtras
            MaestroIDE
            MaestroIndent
            MaestroMeta
            BaseMaestro
            BasePlugin[PyodideMacrosConfig]
            MacrosPlugin                        <<< Meta configs also must be seen here!
            BasePlugin
            Generic
        """

        mro_depth = { cls.__qualname__: i for i,cls in enumerate(self.__class__.mro()) }
        no_wrapper_depth = mro_depth['BasePlugin']
        for hook in '''
            on_pre_page
            on_page_read_source
            on_page_markdown
            on_page_content
            on_page_context
            on_post_page
        '''.split():
            method = getattr(self, hook, None)
            if not method:
                continue

            cls_qualname = method.__qualname__[:-len(method.__name__)-1]
            need_wrapper = mro_depth[cls_qualname] < no_wrapper_depth

            if need_wrapper and not hasattr(method, self.__pmt_meta_wrapped__):
                raise PyodideMacrosMetaError(
                    f'The { method.__qualname__ } event method should be decorated with the '
                    f'pyodide_mkdocs_theme.pyodide_macros.{ self.meta_config_swap.__qualname__ } '
                     'class method decorator (use it as outer decorator).'
                )


    #-------------------------------------------------------------------------


    @classmethod
    def meta_config_swap(cls, method):
        """
        Static decorator for mkdocs events that are using a Page argument.

        For the decorated event, the global mkdocs config content will be swapped with a version
        of it merged with the content of the .meta.pmt.yml files, and any metadata section in the
        page itself.
        """

        page_getter = None  # extract the Page argument from the hook call arguments

        def build_page_getter(self, args, kwargs):
            nonlocal page_getter

            i_arg = next((i for i,v in enumerate(args) if isinstance(v,Page)), None)
            name  = next( (name for name,v in kwargs.items() if isinstance(v,Page)), None)
            # pylint: disable=unnecessary-lambda-assignment
            if i_arg is not None:
                page_getter = lambda args, _: args[i_arg]
            elif name is not None:
                page_getter = lambda _,kwargs: kwargs[name]
            else:
                raise PyodideMacrosMetaError(
                    "Couldn't find an argument whose the value is a mkdocs Page instance on "
                    f"the { method.__name__ } method of { self }"
                )
            return page_getter


        @wraps(method)
        def wrapper(self:MaestroMeta, *a, **kw):
            page: Page   = ( page_getter or build_page_getter(self,a,kw) )(a, kw)
            current_conf = self.config
            meta_config  = self._meta_tree.get_config_for_page_with_metadata(page)      # pylint: disable=protected-access
            self.config  = meta_config
            try:
                out = method(self, *a,**kw)
            finally:
                self.config = current_conf
            return out

        setattr(wrapper, cls.__pmt_meta_wrapped__, True)
        return wrapper



    def apply_macro(self, name, func, *args, **kwargs):            # pylint: disable=unused-argument
        """ Apply all default arguments from the current config """

        arg_config = ARGS_MACRO_CONFIG.get_sub_config_if_exist(name)

        if arg_config:
            for arg_name, arg in arg_config.args.items():
                if not arg.in_config:
                    continue
                if arg.is_positional and arg.index >= len(args):
                    args += ( arg.get_value(self), )
                elif not arg.is_positional and arg_name not in kwargs:
                    kwargs[arg_name] = arg.get_value(self)

        return super().apply_macro(name, func, *args, **kwargs)





@dataclass
class MetaTree:

    segment: str
    """ Directory name or file name. """

    config: CopyableConfig

    children: Dict[str,'MetaTree'] = field(default_factory=dict)

    _cache: ClassVar[Dict[str,Any]] = {}


    @classmethod
    def create(cls, config:PyodideMacrosConfig):

        cls._cache.clear()

        # Remove anything that is invalid for a PyodideMacrosConfig instance => allow to get rid of
        # the macro related parts and various thing that shouldn't be there...
        #
        # TODO: this has become pointless, I think... => to remove + test without it.
        # note: get rid of the classmethod on the way? (using a marker on the segment argument? meh...)
        cfg:PyodideMacrosConfig = PyodideMacrosConfig()
        cfg = cfg.copy_with(config)
        return cls('_docs_', cfg)


    def insert_meta_file(self, yml_dct:dict, meta_path:Path, docs_dir:Path):

        tree = self
        for segment in meta_path.parent.parts:
            if segment not in tree.children:
                tree.children[segment] = MetaTree(segment, tree.config)
            tree = tree.children[segment]
        tree.config = tree.config.copy_with(yml_dct, consume_dict=True)

        if yml_dct:
            raise BuildError(
                f"Invalid content in { docs_dir / meta_path }:"
                + "".join( f'\n    {k} : {v!r}' for k,v in yml_dct.items())
            )



    def get_config_for_page_with_metadata(self, page:Page):
        """
        Extract the appropriated config for the given Page directory, then merge it with
        any metadata section coming from the Page itself.

        NOTE: Only the metadata watching some of the plugin's config options will be merged.
              Other values/items will stay ignored (they are still usable in macros call using
              the original way the macros plugin handles them). For more information, see:
              https://mkdocs-macros-plugin.readthedocs.io/en/latest/post_production/#html-templates
        """
        src = Path(page.file.src_uri)       # Relative to docs_dir!

        if src not in self._cache:
            tree = self
            segments = src.parent.parts     # Note:  Path('index.md').parent.parts == () => ok!
            for segment in segments:
                if segment not in tree.children:
                    break
                tree = tree.children[segment]
            config = tree.config if not page.meta else tree.config.copy_with(page.meta)
            self._cache[src] = config

        return self._cache[src]
