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

from ..maestro_tools import CopyableConfig, DeprecatedMsg, deprecated_option





class BuildConfig(CopyableConfig):
    """ Build configuration options """


    encrypted_js_data = C.Type(bool, default=True)
    """
    If True, the configuration data for IDEs, terminals, py_btns, ... are encrypted. In case of
    decompression troubles, you may want to deactivate this option.

    Note that the ides.encrypt_alpha_mode setting also applies to these encryptions.
    """


    ignore_macros_plugin_diffs = C.Type(bool, default=False)
    """
    Set to True to bypass the compatibility check of the `PyodideMacrosPlugin` config against
    the original `MacrosPlugin` one.

    ??? note "Reasons behind this verification"

        `MacrosPlugin` is configured the "old fashion" way while `PyodideMacrosPlugin` is using
        mkdocs 1.5+ Config classes. This means that the `MacrosPlugin` configuration had to be
        hardcoded in the `PyodideMacrosPlugin` config.

        Because of this, any config change on the `MacrosPlugin` side could break
        `PyodideMacrosPlugin` without warning, so this verification enforces the expected
        implementation of the parent class.

        If ever something unexpected is found, the build will be aborted, because no guarantees
        can be given about the correctness of the build in such situation.

        In case of minor changes, this option will allow the build, but use it "at your own risks".
    """

    forbid_macros_override = C.Type(bool, default=True)
    """
    If True, `PyodideMacrosError` is raised when two macros are registered with the same name.
    """

    skip_py_md_paths_names_validation = C.Type(bool, default=False)
    """
    By default, the path names of all the `.py` and `.md` files present in the docs_dir are
    checked so that they do not contain any character other than letters, digits, dots or dashes.
    This ensures the macros related to IDEs will work properly.

    If unwanted characters are found, a BuildError is raised, but this verification can be turned
    off by setting this flag to True. Use it at your own risks.
    """

    python_libs = C.ListOfItems(C.Type(str), default=['py_libs'])
    """
    List of directories of python packages that must be importable in Pyodide.

    An error is raised if:

    * The given name isn't an existing directory (unless it's the default value, `py_libs`)
    * The directory isn't at project root level
    * The directory isn't a python package (aka: it must have an `__init__.py` file).
    """

    load_yaml_encoding = C.Type(str, default='utf-8')
    """
    Encoding to use when loading yaml data with the original MacrosPlugin functionalities :

    The original method doesn't use any encoding argument, which can lead to different behaviors
    between Windows and Linux (typically: during a pipeline vs working locally with Windows).
    """

    macros_with_indents = C.ListOfItems(C.Type(str), default=[])
    """
    Allow to register external macros, as a list of strings, that will need to insert properly
    indented multiline contents in the page.
    Once a macro is registered in this list, it can call `env.get_macro_indent()` at runtime to get
    the indentation level (as a string of spaces) of the macro call in the markdown source file.
    """

    tab_to_spaces = C.Type(int, default=-1)
    """
    If set to a positive value (or 0), tabs characters found before a call to a multiline macro
    will automatically be converted using this number of spaces (see [`macros_with_indent`](
    --pyodide_mkdocs_theme_pyodide_macros_plugin_config_BuildConfig_macros_with_indents) option).
    <br>_There are NO guarantees about the correctness of the result_.

    If a conversion is done, a warning will be shown in the console to find and modify more easily
    the problematic macros calls.
    """

    meta_yaml_encoding = C.Type(str, default='utf-8')
    """ Encoding to use when loading `.meta.pmt.yml` files. """

    _pmt_meta_filename = C.Type(str, default=".meta.pmt.yml")
    """ Name used for the Pyodide-MkDoc-Theme meta files. """


    deprecation_level = C.Choice( ('error', 'warn'), default='error')
    """ Behavior when a deprecated feature is used. """


    #----------------------------------------------------------------------------


    encrypt_corrections_and_rems = deprecated_option(
        'ides.encrypt_corrections_and_rems', bool, DeprecatedMsg.moved,
        src='build.encrypt_corrections_and_rems',
    )
    """
    If True, the html div under IDEs containing correction and remarks will be encrypted at build
    time.

    Passing this to False can be useful during development, but value should _ALWAYS_ be set
    to true on the deployed website: keep in mind the search engine can otherwise make surface
    contents from corrections and remarks as suggestions when the user is using the search bar.
    """

    forbid_secrets_without_corr_or_REMs = deprecated_option(
        'ides.forbid_secrets_without_corr_or_REMs', bool, DeprecatedMsg.moved,
        src='build.forbid_secrets_without_corr_or_REMs',
    )
    """
    By default, this situation is considered invalid and `BuildError` will be raised.
    If this is the desired behavior, set this option to false.
    """

    forbid_hidden_corr_and_REMs_without_secrets = deprecated_option(
        'ides.forbid_hidden_corr_and_REMs_without_secrets', bool, DeprecatedMsg.moved,
        src='build.forbid_hidden_corr_and_REMs_without_secrets',
    )
    """
    When building IDEs, the validation button will appear only when a `secrets` section exist.
    If none is given while a corr section or REM files exist, their content will never be available
    to the user because of the lack of validation button in the interface.

    By default, this situation is considered invalid and `BuildError` will be raised.
    If this is the desired behavior, set this option to false.
    """

    forbid_corr_and_REMs_with_infinite_attempts = deprecated_option(
        'ides.forbid_corr_and_REMs_with_infinite_attempts', bool, DeprecatedMsg.moved,
        src='build.forbid_corr_and_REMs_with_infinite_attempts',
    )
    """
    When building IDEs, if a `corr` section, a REM file or a VIS_REM file exist while the number
    of attempts is infinite, that content will never become accessible to the user, unless they
    pass the tests.

    By default, this situation is considered invalid and `BuildError` will be raised.
    If this is the desired behavior, set this option to false.
    """

    bypass_indent_errors = deprecated_option('build.bypass_indent_errors', bool, DeprecatedMsg.removed)
    """
    _DEPRECATED: This option shouldn't be needed anymore._

    If True, all errors raised when trying to find what is the indentation level of a macro call
    are bypassed and a message is instead printed to the console.

    The purpose of this option is _not_ to deactivate the securities, but to allow gathering info
    about all the indentation problems at once: the resulting markdown content will most likely be
    incorrect and be rendered with unexpected results.
    """

    # check_python_files = C.Type(bool, default=False)
    # """
    # If True, the different sections of the python files will be tested against each others during
    # the build and provide feedback in the console.

    # Unless the `soft_check` option is used, a BuildError will be raised if something considered
    # wrong happens. See the documentation for more details.

    # Warning:
    #     - This is totally independent from the pyodide environment. For example, it won't
    #       give any warning if a forbidden function is used in the tests (which will fail
    #       on the website).
    #     - These verifications __considerably increase the build time__ (expect something
    #       around x10).
    # """

    # soft_check = C.Type(bool, default=True)
    # """
    # If True and `check_python_files` is also True, the python sections are verified, but the
    # build won't be interrupted if something wrong or suspicious is discovered: a message will
    # instead be displayed in the console.
    # """





class IdesConfig(CopyableConfig):
    """ All options related to validation tests (IDEs) """

    encrypt_corrections_and_rems = C.Type(bool, default=True)
    """
    If True, the html div under IDEs containing correction and remarks will be encrypted at build
    time.

    Passing this to False can be useful during development, but value should _ALWAYS_ be set
    to true on the deployed website: keep in mind the search engine can otherwise make surface
    contents from corrections and remarks as suggestions when the user is using the search bar.
    """

    encrypt_alpha_mode = C.Choice(('shuffle', 'direct', 'sort'), default='direct')
    """
    Determine how the alphabet for the LZW compression is built, from the content to encode:

    - `"shuffle"`: the alphabet is randomized.
    - `"direct"`: the alphabet is using all symbols in order.
    - `"sort"`: the alphabet sorting all symbols in natural order.
    """

    forbid_secrets_without_corr_or_REMs = C.Type(bool, default=True)
    """
    By default, this situation is considered invalid and `BuildError` will be raised.
    If this is the desired behavior, set this option to false.
    """

    forbid_hidden_corr_and_REMs_without_secrets = C.Type(bool, default=True)
    """
    When building IDEs, the validation button will appear only when a `secrets` section exist.
    If none is given while a corr section or REM files exist, their content will never be available
    to the user because of the lack of validation button in the interface.

    By default, this situation is considered invalid and `BuildError` will be raised.
    If this is the desired behavior, set this option to false.
    """

    forbid_corr_and_REMs_with_infinite_attempts = C.Type(bool, default=True)
    """
    When building IDEs, if a `corr` section, a REM file or a VIS_REM file exist while the number
    of attempts is infinite, that content will never become accessible to the user, unless they
    pass the tests.

    By default, this situation is considered invalid and `BuildError` will be raised.
    If this is the desired behavior, set this option to false.
    """

    decrease_attempts_on_user_code_failure = C.Type(bool, default=True)
    """
    If true, any failure when running the user code during a validation will decrease the number
    of attempts left. Note this means even syntax errors will decrease the count.

    When this option is set to True, any error raised within the code of the editor will stop
    the validation process without modifying the number of attempts left.
    """

    deactivate_stdout_for_secrets = C.Type(bool, default=True)
    """
    Define if the stdout will be shown to the user or not, for the secret tests.
    """

    show_only_assertion_errors_for_secrets = C.Type(bool, default=False)
    """
    If True, the stack trace of all error messages will be suppressed and only assertion messages
    will be left unchanged, when an error is raised during the secret tests.
    """

    #--------------------------------------------------------------------------------


    show_assertion_code_on_failed_test = deprecated_option(
        'args.IDE.LOGS',bool,DeprecatedMsg.moved, src='ides.show_assertion_code_on_failed_test'
    )
    """
    When an assertion fails in the secret tests and that assertion doesn't have any assertion
    message, the code of the assertion itself will be displayed in the terminal if this option
    is set to True (default).

    This behavior is global, but can be overridden on a "per IDE" base, using the `auto_log_assert`
    optional argument.
    """

    max_attempts_before_corr_available = deprecated_option(
        'args.IDE.MAX',int, DeprecatedMsg.moved, src='ides.max_attempts_before_corr_available'
    )
    """
    Global setting for all IDE in the documentation: max number of tries a user can do before
    correction and remarks become available (reminder: they are in a collapsed details/admonition,
    requiring the user to click to reveal the content. This way, they can still try to get the code
    right without actually seeing the solution, before actually giving up).

    NOTE: using 1000 will result in an infinite number of attempts (ie. corr and REMs contents will
    never become available if any).

    This behavior is global, but can be overridden on a "per IDE" base, using the `MAX` optional
    argument.
    """

    default_ide_height_lines = deprecated_option(
        'args.IDE.MAX_SIZE', int, DeprecatedMsg.moved, src='ides.default_ide_height_lines'
    )
    """
    Max height of the editor (in number of lines). For the macro IDEv, this takes precedence on
    the TERM_H argument of the terminal.
    """





class TermsConfig(CopyableConfig):
    """ Terminals configuration options """

    stdout_cut_off = C.Type(int, default=200)
    """
    Maximum number of lines displayed at once in a terminal. If more lines are printed, the
    lines at the top are removed.

    NOTE: jQuery.terminals become AWFULLY SLOW when the number of characters they display
    become somewhat massive. This option allows to limit these performances troubles, when
    the stdout is not truncated (see terminals upper right corner button). Also note that
    this option _does not_ limit the number of characters per line, so a frozen page can
    still occur, while the truncation feature will take care of that.
    """

    cut_feedback = C.Type(bool, default=True)
    """
    If True, the content printed in the terminal will be truncated if it's too long, to avoid
    performances troubles.
    """

    #--------------------------------------------------------------------------------

    default_height_ide_term = deprecated_option(
        'args.IDE.TERM_H', int, DeprecatedMsg.moved, src="terms.default_height_ide_term",
    )

    default_height_isolated_term = deprecated_option(
        'args.terminal.TERM_H', int, DeprecatedMsg.moved, src="terms.default_height_isolated_term",
    )





class QcmsConfig(CopyableConfig):
    """ Options specific to the QCMs or QCSs"""

    hide    = deprecated_option('args.multi_qcm.hide', bool, DeprecatedMsg.moved, src="qcms.hide")
    multi   = deprecated_option('args.multi_qcm.multi', bool, DeprecatedMsg.moved, src="qcms.multi")
    shuffle = deprecated_option('args.multi_qcm.shuffle', bool, DeprecatedMsg.moved, src="qcms.shuffle")

    forbid_no_correct_answers_with_multi = C.Type(bool, default=False)
    """
    If False, a question with no correct answer provided, but that is tagged as `multi=True`
    is considered valid. If this option is set to True, that situation will raise an error.
    """



class OtherConfig(CopyableConfig):
    """ Options used in the macros that have not been updated yet """

    scripts_url = deprecated_option('scripts_url', str, DeprecatedMsg.unsupported_macro)
    site_root   = deprecated_option('site_root', str, DeprecatedMsg.unsupported_macro)
