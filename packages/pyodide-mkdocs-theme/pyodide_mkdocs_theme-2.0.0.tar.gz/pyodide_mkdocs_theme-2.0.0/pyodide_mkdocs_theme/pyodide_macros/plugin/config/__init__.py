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


from mkdocs.config import config_options as C
from mkdocs_macros.plugin import MacrosPlugin

from ..maestro_tools import CopyableConfig
from .args_macros_config import ARGS_MACRO_CONFIG
from ._mkdocs_sub_configs import BuildConfig, IdesConfig, TermsConfig, QcmsConfig, OtherConfig



# Verify if something changed on the MacrosPlugin side... (moved to on_startup)
# Current setup for MacrosPlugin v1.0.4

_EXPECTED_MACRO_CONF = set("""
    module_name
    modules
    render_by_default
    include_dir
    include_yaml
    j2_block_start_string
    j2_block_end_string
    j2_variable_start_string
    j2_variable_end_string
    on_undefined
    on_error_fail
    verbose
""".split())

_SRC_MACROS_CONF = dict(MacrosPlugin.config_scheme)

_MISSING_MACROS_PLUGIN_PROPS = _EXPECTED_MACRO_CONF - set(_SRC_MACROS_CONF)
MISSING_MACROS_PROPS = (
    "" if not _MISSING_MACROS_PLUGIN_PROPS else "\nDisappeared from MacrosPlugin:" + ''.join(
        f'\n\t{name}' for name in _MISSING_MACROS_PLUGIN_PROPS
    )
)

_NEW_MACROS_PLUGIN_PROPS = set(_SRC_MACROS_CONF) - _EXPECTED_MACRO_CONF
EXTRAS_MACROS_PROPS = (
    "" if not _NEW_MACROS_PLUGIN_PROPS else "\nNew config in MacrosPlugin:" + ''.join(
        f'\n\t{name}' for name in _NEW_MACROS_PLUGIN_PROPS
    )
)


J2_STRING                  = _SRC_MACROS_CONF['include_dir'].default
DEFAULT_MODULE_NAME        = _SRC_MACROS_CONF['module_name'].default
DEFAULT_UNDEFINED_BEHAVIOR = _SRC_MACROS_CONF['on_undefined'].default







# This only defines the values exposed to the user in mkdocs.yml.
# When a property is declared here, don't forgot to add the related extractor on the
# BaseMaestro class.
class PyodideMacrosConfig(CopyableConfig):
    """ Configuration for the main pyodide-mkdocs-theme plugin. """

    _dev_mode = C.Type(bool, default=False)
    """ Run the plugin in development mode (...don't use that). """

    args = ARGS_MACRO_CONFIG.to_config()
    """ Macros arguments configuration (see use of `.met.pmt.yml` files and metadata headers). """

    build = C.SubConfig(BuildConfig)
    """ Build related options """

    ides = C.SubConfig(IdesConfig)
    """ Configuration related to the validation tests in IDEs """

    terms = C.SubConfig(TermsConfig)
    """ Configuration related to the terminals """

    qcms = C.SubConfig(QcmsConfig)
    """ QCMs related options """

    _others = C.SubConfig(OtherConfig)
    """ Old configuration options (unmaintained, so far) """

    # ---------------------------------------------------------------------------------------
    # Replication of MacrosPlugin options (merging the config_scheme properties programmatically
    # is not enough, unfortunately...)


    render_by_default        = C.Type(bool, default=True)
    """
    Render macros on all pages by default. If set to false, sets an opt-in mode where only pages
    marked with render_macros: true in header will be displayed.
    """
    module_name              = C.Type(str,  default=DEFAULT_MODULE_NAME)
    """
    Name of the Python module containing macros, filters and variables. Indicate the file or
    directory, without extension; you may specify a path (e.g. include/module). If no main
    module is available, it is ignored.
    """
    modules                  = C.Type(list, default=[])
    """
    List of pluglets to be added to mkdocs-macros (preinstalled Python modules that can be listed
    by pip list).
    """
    include_dir              = C.Type(str,  default=J2_STRING)
    """ Directory for including external files """
    include_yaml             = C.Type(list, default=[])
    """ Non-standard Jinja2 marker for start of block """
    j2_block_start_string    = C.Type(str,  default=J2_STRING)
    """ Non-standard Jinja2 marker for start of variable """
    j2_block_end_string      = C.Type(str,  default=J2_STRING)
    """ Non-standard Jinja2 marker for end of block """
    j2_variable_start_string = C.Type(str,  default=J2_STRING)
    """ Non-standard Jinja2 marker for end of variable """
    j2_variable_end_string   = C.Type(str,  default=J2_STRING)
    """ Non-standard Jinja2 marker for end of variable """
    on_error_fail            = C.Type(bool, default=False)
    """
    Make the building process fail in case of an error in macro rendering (this is useful when
    the website is rebuilt automatically and errors must be detected.)
    """
    on_undefined             = C.Type(str,  default=DEFAULT_UNDEFINED_BEHAVIOR)
    """
    Behavior of the macros renderer in case of an undefined variable in a page. By default, it
    leaves the Jinja2 statement untouched (e.g. {{ foo }} will appear as such in the page.) Use
    the value 'strict' to make it fail.
    """
    verbose                  = C.Type(bool, default=False)
    """ Print debug (more detailed) statements in the console. """
