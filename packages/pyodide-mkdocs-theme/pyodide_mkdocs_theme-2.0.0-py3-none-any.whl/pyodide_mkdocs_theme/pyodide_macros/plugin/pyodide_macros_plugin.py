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


import os
import re
from operator import attrgetter
from collections import Counter, defaultdict
from functools import wraps
from pathlib import Path
from typing import Dict, List


from mkdocs.structure.files import Files
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import BuildError
from mkdocs_macros.plugin import MacrosPlugin


from ...__version__ import __version__
from ..exceptions import PyodideConfigurationError, PyodideMacrosPyLibsError
from ..pyodide_logger import logger
from ..macros import (
    autres,
    IDEs,
    isolated_components,
    qcm,
)
from .config.args_macros_config import ARGS_MACRO_CONFIG, ArgConfig
from .config import MISSING_MACROS_PROPS, EXTRAS_MACROS_PROPS
from .maestro_tools import DeprecationDelayedError, PythonLib
from .maestro_base import BaseMaestro
from .maestro_meta import MaestroMeta
from .maestro_indent import MaestroIndent
from .maestro_IDE import MaestroIDE
from .maestro_extras import MaestroExtras







class PyodideMacrosPlugin(
    MaestroExtras,
    MaestroIDE,
    MaestroIndent,
    MaestroMeta,
    BaseMaestro,
    MacrosPlugin,    # Always last, so that other classes may trigger super methods appropriately.
):
    """
    Class centralizing all the behaviors of the different parent classes.

    This is kinda the "controller", linking all the behaviors to mkdocs machinery, while the
    parent classes hold the "somewhat self contained" behaviors.

    For reference, here are the hooks defined in the original MacrosPlugin:
        - on_config
        - on_nav
        - on_page_markdown  (+ on_pre_page_macros + on_post_page_macros)
        - on_post_build     (on_post_build macros)
        - on_serve
    """

    libs: List[PythonLib]


    # Override
    def on_config(self, config:MkDocsConfig):
        # pylint: disable=attribute-defined-outside-init

        # --------------------------------------------------------------
        # Section to always apply first:

        self._conf    = config # done in MacrosPlugin, but also done here because needed here or there

        self.docs_dir_path    = Path(config.docs_dir)
        self.docs_dir_cwd_rel = self.docs_dir_path.relative_to(Path.cwd())

        # --------------------------------------------------------------

        self._check_macros_plugin_props()
        self._check_docs_paths_validity()
        self._transfer_old_options_to_args()

        super().on_config(config)

        DeprecationDelayedError.handle_deprecations(self)
        self._handle_python_libs()




    def on_files(self, files: Files, /, *, config: MkDocsConfig):
        """
        If python libs directories are registered, create one archive for each of them.
        It's on the responsibility of the user to work with them correctly...
        """
        for lib in self.libs:
            # Remove any cached files to make the archive lighter (the version won't match
            # pyodide compiler anyway!):
            for cached in lib.path.rglob("*.pyc"):
                cached.unlink()
            file = lib.create_archive_and_get_file(self)
            files.append(file)



    # Override
    def on_post_build(self, config: MkDocsConfig) -> None:
        """
        Suppress the python archives from the CWD.
        """
        for lib in self.libs:
            lib.unlink()

        super().on_post_build(config)


    #--------------------------------------------------------------------------



    # Override
    def _load_modules(self):
        """ Override the super method to register the Pyodide macros at appropriate time """

        def macro_with_warning(func):
            macro = func(self)
            logged = False          # log once only only per macro...

            @wraps(func)
            def wrapper(*a,**kw):
                nonlocal logged
                if not logged:
                    logged = True
                    self.warn_unmaintained(f'The macro {func.__name__!r}')
                return macro(*a,**kw)
            return wrapper


        macros = [
            IDEs.IDE,
            IDEs.IDEv,
            IDEs.terminal,
            IDEs.py_btn,
            IDEs.section,

            qcm.multi_qcm,

            isolated_components.py,
            isolated_components.figure,
        ]
        old_macros = [
            autres.cours,
            autres.exercice,
            autres.ext,
            autres.html_fig,
            autres.numworks,
            autres.python_carnet,
            autres.python_ide,
            autres.tit,
            autres.mult_col,
        ]

        for func in macros:
            self.macro(func(self))

        for func in old_macros:
            self.macro( macro_with_warning(func) )

        super()._load_modules()



    # Override
    def _load_yaml(self):
        """
        Override the MacrosPlugin method, replacing on the fly `__builtins__.open` with a version
        handling the encoding.
        """
        # pylint: disable=multiple-statements
        src_open = open
        def open_with_utf8(*a,**kw):
            return src_open(*a,**kw, encoding=self.load_yaml_encoding)

        # Depending on the python version/context, the __builtins__ can be of different types
        as_dct = isinstance(__builtins__, dict)

        if as_dct:  __builtins__['open'] = open_with_utf8
        else:       __builtins__.open = open_with_utf8
        try:
            super()._load_yaml()
        finally:
            if as_dct:  __builtins__['open'] = src_open
            else:       __builtins__.open = src_open



    #--------------------------------------------------------------------------



    def _check_docs_paths_validity(self) -> None :
        """
        Travel through all paths in the docs_dir and raises an BuildError if "special characters"
        are found in directory, py, or md file names (accepted characters are: r'[\\w.-]+' )
        """
        if self.skip_py_md_paths_names_validation:
            logger.debug("Skipped markdown path names validation.")
            return
        logger.debug("Markdown path names validation.")

        invalid_chars = re.compile(r'[^A-Za-z0-9_.-]+')
        wrongs = defaultdict(list)

        # Validation is done on the individual/current segments of the paths, so that an invalid
        # directory name is not affecting the validation of its children.
        for path,dirs,files in os.walk(self.docs_dir):
            files_to_check = [ file for file in files if re.search(r'\.(py|md)$', file)]
            for segment in dirs + files_to_check:
                invalids = frozenset(invalid_chars.findall(segment))
                if invalids:
                    wrongs[invalids].append( os.path.join(path,segment) )

        if wrongs:
            msg = ''.join(
                f"\nInvalid characters {repr(''.join(sorted(invalids)))} found in these filepaths:"
                + "".join(f"\n\t{ path }" for path in sorted(lst))
                for invalids,lst in wrongs.items()
            )
            raise BuildError(
                f"{ msg }\nPython and markdown files, and their parent directories' names "
                'should only contain alphanumerical characters (no accents or special chars), '
                "dots, underscores, and/or hyphens."
            )



    def _check_macros_plugin_props(self):
        """ Verify that the config of the MacroPlugin class is still the expected one """
        logger.debug("Check that the original MacrosPlugin implementation didn't change.")

        if not MISSING_MACROS_PROPS and not EXTRAS_MACROS_PROPS:
            return

        if self.ignore_macros_plugin_diffs:
            logger.error(
                "Inconsistent MacrosPlugin properties. `build.ignore_macros_plugin_diffs` "
                "is set to true"
            )

        else:
            raise PyodideConfigurationError(f"""
Cannot configure PyodideMacrosPlugin: the basic configuration of MacrosPlugin changed:
{MISSING_MACROS_PROPS}{EXTRAS_MACROS_PROPS}"""
"\nIf you absolutely need to run mkdocs before any fix is done, you can try the option "
"`ignore_macros_plugin_diffs: true` in the `plugin_macros` section of `mkdocs.yml`, "
"but there are no guarantees the build will succeed, depending on what the changes were.\n\n")



    def _transfer_old_options_to_args(self):
        """
        Explore the MacrosConfig hierarchy and automatically transfer non None values from
        deprecated options to their new location.
        Apply the same logic for other config options that were moved and are now deprecated.
        """
        logger.debug("Options backward compatibility")

        def parent_and_val(path, *, assign=None, arg:ArgConfig=None):
            parent,stuff = None, self.config
            for attr in path:
                parent,stuff = stuff, getattr(stuff, attr, None)
                if stuff is None:
                    return None
            if assign is not None:
                if arg:
                    assign = arg.process_value_from_old_location(assign)
                setattr(parent, path[-1], assign)
            return stuff

        def reassign_deprecated_prop(src_path, target_path, arg=None):
            val = parent_and_val(src_path)
            if val is not None:
                logger.info(f"Reassign { '.'.join(src_path) } to { '.'.join(target_path) }")
                parent_and_val(target_path, assign=val, arg=arg)

        #----------------------------

        for arg,path in ARGS_MACRO_CONFIG.args_with_tree_path_as_gen():
            if arg.deprecated_source:
                reassign_deprecated_prop(arg.deprecated_source, path, arg)

        for prop in """
            encrypt_corrections_and_rems
            forbid_secrets_without_corr_or_REMs
            forbid_hidden_corr_and_REMs_without_secrets
            forbid_corr_and_REMs_with_infinite_attempts
        """.split():
            reassign_deprecated_prop(('build',prop), ('ides',prop))




    def _handle_python_libs(self):
        """
        Add the python_libs directory to the watch list, create the internal PythonLib objects,
        and check python_libs validity:
            1. No python_lib inside another.
            2. If not a root level, must not be importable.
            3. No two python libs with the same name (if registered at different levels)
        """

        self._conf.watch.extend(
            str(py_lib.absolute()) for py_lib in map(Path, self.python_libs)
                                   if py_lib.exists()
        )

        self.libs = sorted(
            filter(bool, map(PythonLib, self.python_libs)), key=attrgetter('abs_slash')
        )


        libs_by_name: Dict[str, List[PythonLib]] = defaultdict(list)
        for lib in self.libs:
            libs_by_name[lib.lib_name].append(lib)


        same_names = ''.join(
            f"\nLibraries that would be imported as {name!r}:" + ''.join(
                f'\n\t{ lib.lib }' for lib in libs
            )
            for name,libs in libs_by_name.items() if len(libs)>1
        )
        if same_names:
            raise PyodideMacrosPyLibsError(
                "Several custom python libs will end up with the same final name. This is not allowed."
                + same_names
            )


        parenting = ''.join(
            f"\n\t{ self.libs[i-1].lib } contains at least { lib.lib }"
                for i,lib in enumerate(self.libs)
                if i and self.libs[i-1].is_parent_of(lib)
        )
        if parenting:
            raise PyodideMacrosPyLibsError(
                "Custom python libs defined in the project cannot contain others:" + parenting
            )
