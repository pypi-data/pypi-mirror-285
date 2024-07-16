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

# pylint: disable=unused-argument



from typing import ClassVar, Tuple, Union
from itertools import compress
from dataclasses import dataclass
from math import inf

from .. import html_builder as Html
from ..tools_and_constants import HtmlClass, IdeConstants, Kinds, Prefix, IdeMode, ScriptKind
from ..messages import Tip
from ..parsing import build_code_fence, items_comma_joiner
from ..paths_utils import convert_url_to_utf8, to_uri

from .ide_manager import IdeManager




#---------------------------------------------------------------------------------





@dataclass
class Ide(IdeManager):
    """
    Builds an editor + a terminal + the buttons and extra logistic needed for them.
    """

    ID_PREFIX: ClassVar[str] = Prefix.editor_

    NEED_INDENTS: ClassVar[bool] = True

    NEEDED_KINDS: ClassVar[Tuple[ScriptKind]] = Kinds.pyodide, Kinds.terms, Kinds.ides

    KW_TO_TRANSFER: ClassVar[Tuple[Tuple[str,str]]] = (
        ('MAX',     'max_attempts'),
        ('MAX_SIZE','max_size'),
        ('LOGS',    'auto_log_assert'),
        ('TERM_H',  'term_height'),
        ('MODE',    'profile'),
    )

    JS_EXPORTED_VALUES: ClassVar[set] = set('''
        profile
        corr_content
        attempts_left
        auto_log_assert
        corr_rems_mask
        has_check_btn
        max_ide_lines
        is_vert
        is_encrypted
        decrease_attempts_on_code_error
        deactivate_stdout_for_secrets
        show_only_assertion_errors_for_secrets
        stdout_cut_off
    '''.split())




    @property
    def keep_corr_on_export(self):
        return self.env.in_serve




    def _validate_files_config(self, max_attempts: Union[int,float] ):

        if self.profile is not None:
            return

        msg = prop = None

        if(
            self.env.forbid_secrets_without_corr_or_REMs
            and self.has_secrets and not self.has_any_corr_rems
        ):
            msg = "A `secrets` section exist but there are no `corr` section, REM or VIS_REM file."
            prop = "ides.forbid_secrets_without_corr_or_REMs"

        elif(
            self.env.forbid_hidden_corr_and_REMs_without_secrets
            and self.has_any_corr_rems and not self.has_secrets
        ):
            elt_msg = self._get_corr_rems_msg()
            msg     = f"{ elt_msg }, but there is no `secrets` section."
            prop    = 'ides.forbid_hidden_corr_and_REMs_without_secrets'

        elif(
            self.env.forbid_corr_and_REMs_with_infinite_attempts
            and self.has_any_corr_rems and max_attempts==inf
        ):
            elt_msg = self._get_corr_rems_msg()
            msg     = (f"{ elt_msg } but will never be visible because the number of "
                      +"attempts is set to infinity.")
            prop    = 'ides.forbid_corr_and_REMs_with_infinite_attempts'

        self._validation_outcome(msg,prop)



    def _get_corr_rems_msg(self, present:bool=True):
        elements = [*filter(bool,(
            "a correction"   * (present == self.has_corr),
            "a REM file"     * (present == self.has_rem),
            "a VIS_REM file" * (present == self.has_vis_rem),
        ))]
        elt_msg = items_comma_joiner(elements, 'and')
        single  = len(elements)==1
        verb    = f"exist{ 's' * (single)}" if present else f"{ 'is' if single else 'are' } missing"
        elt_msg = f"{ elt_msg } { verb }".capitalize()
        return elt_msg





    def generate_id(self):
        """
        Generate an id number for the current IDE (editor+terminal), as a "prefix_hash(32bits)".

        This id must be:
            - Unique to every IDE used throughout the whole website.
            - Stable, so that it can be used to identify what IDE goes with what file or what
              localStorage data.

        Current strategy:
            - If the file exists, hash its path.
            - If there is no file, use the current global IDE_counter and hash its value as string.
            - The "mode" of the IDE is appended to the string before hashing.
            - Any ID value (macro argument) is also appended to the string before hashing.

        Uniqueness of the resulting hash is verified and a BuildError is raised if two identical
        hashes are encountered.
        """
        py_path = self.files_data.exo_py
        if py_path:
            path = str(py_path)
        else:
            path = str(self.env.ide_count)

        if self.mode:
            path += self.mode       # legacy...

        if self.id is not None:
            path += str(self.id)

        return self.id_to_hash(path)



    def make_element(self) -> str:
        """
        Create an IDE (Editor+Terminal+buttons) within an Mkdocs document. {py_name}.py
        is loaded in the editor if present.
        """
        ide_layout = self.generate_empty_ide()
        buttons    = self.generate_buttons_row()

        global_layout = Html.div(
            ide_layout + buttons,
            id = f"{ Prefix.global_ }{ self.editor_name }",
            kls = HtmlClass.py_mk_ide,
        )
        solution_div = self._build_corr_and_rems()
        return global_layout + solution_div
        # The solution_div not inside the other because markdown rendering troubles otherwise
        # (because of "md_in_html"). Also it will become useful as "anchor" for IDE extractions
        # and insertions, when/if ever the "full screen" mode is implemented.
        #
        # NOTE about indentations : global_layout + the beginning of solution_div is a unique,
        #      long-ass string of html only, so everything is still properly indented, as long
        #      as all this is still the very beginning of the returned string.



    def generate_empty_ide(self) -> str:
        """
        Generate the global layout that will receive later the ace elements.
        """
        is_v = self.mode == '_v'
        toggle_txt = '###'
        tip: Tip = self.env.lang.comments
        msg = str(tip)

        shortcut_comment_asserts = Html.span(
            toggle_txt + Html.tooltip(msg, tip.em, shift=95),
            id = Prefix.comment_ + self.editor_name,
            kls = f'{HtmlClass.comment} {HtmlClass.tooltip}',
        )
        editor_div = Html.div(
            id = self.editor_name,
            is_v = str(is_v).lower(),
            mode = self.mode,
        )
        editor_wrapper = Html.div(
            editor_div + shortcut_comment_asserts,
            kls = Prefix.comment_ + HtmlClass.py_mk_wrapper
        )

        terminal_div = Html.terminal(
            Prefix.term_ + self.editor_name ,
            kls = f"{ HtmlClass.term_editor }{ self.mode }",
            n_lines_h = self.term_height * (not is_v),
            is_v = is_v,
            env = self.env,
        )

        return Html.div(
            f"{ editor_wrapper }{ terminal_div }",
            kls = f"{ HtmlClass.py_mk_wrapper }{ self.mode }",
        )





    def _build_corr_and_rems(self):
        """
        Build the correction and REM holders. The rendered template is something like the
        following, with the indentation level of the most outer div equal to the indentation
        level of the IDE macro text in the markdown file.
        Depending on the presence/absence of corr, REM and VIS_REM files, some elements may
        be missing, BUT, the outer div will always be created, to simplify the logic on the
        JS layer (this way, the elements are always present in the DOM).

        | var | meaning |
        |-|-|
        | `at_least_one` | corr and/or REM (=> inside admonition) |
        | `anything` | corr or REM or VIS_REM |

        Overall structure of the generated markdown (mixed with html):

                <div markdown="1" id="solution_editor_id"       <<< ALWAYS
                     class="py_mk_hidden" >

                ENCRYPTION_TOKEN                                <<< at least one and encryption ON

                ??? tip "Solution"                              <<< at least one

                    <p></p>                                     <<< Spacer (thx mkdocs... :roll_eyes: )

                    ```python linenums="1"'                     <<< solution
                    --8<-- "{ corr_uri }"                       <<< solution
                    ```                                         <<< solution

                    ___Remarques :___                           <<< remark & solution

                    --8<-- "{ rem_uri }"                        <<< remark

                --8<-- "{ vis_rem_uri }"                        <<< vis_rem

                ENCRYPTION_TOKEN                                <<< at least one and encryption ON

                </div>                                          <<< ALWAYS


        DON'T FORGET:

            1. DON'T EVER PUT HTML TAGS INSIDE ANOTHER ONE THAT ALREADY HAS THE markdown ATTRIBUTE!
            2. Trailing new lines are mandatory to render the "md in html" as expected.
        """

        # Prepare data first (to ease reading of the below sections)
        sol_title = ' & '.join(compress(*zip(
            (str(self.env.lang.title_corr), self.has_corr),
            (str(self.env.lang.title_rem),  self.has_rem)
        )))
        corr_content = self.files_data.corr_content
        at_least_one = self.has_corr or self.has_rem
        anything     = at_least_one or self.has_vis_rem
        with_encrypt = self.env.encrypt_corrections_and_rems and anything
        extra_tokens = ( IdeConstants.encryption_token, ) * with_encrypt


        # Build the whole div content:
        md_div = [         '',   # Extra empty line to enforce proper rendering of the md around
                           f'<div markdown="1" id="{ Prefix.solution_ }{ self.editor_name }" '
                           f'     class="{ HtmlClass.py_mk_hidden }" data-search-exclude >',
                            *extra_tokens ]
        if at_least_one:
            md_div.append( f'??? tip "{ sol_title }"' )
            md_div.append( '    <p></p>' )  # DON'T use an inner html div : it completely brakes
                                            # md rendering when no LZW compression is used.
        if self.has_corr:
            # Inner indented content must be handled now when building the block. The indentation
            # for the current line
            one_level = '    '
            fence = build_code_fence(
                corr_content,
                one_level + self.indentation,
                title=str(self.env.lang.corr)
            )
            md_div.append(  one_level+fence.strip())

        if self.has_corr and self.has_rem:
            rem = self.env.lang.rem
            md_div.append( f'    <span class="{ HtmlClass.rem_fake_h3 }">{ rem } :</span>')

        if self.has_rem:
            rem = self._rem_inclusion('rem_rel_path')
            md_div.append( f'    { rem }' )

        if self.has_vis_rem:
            vis_rem = self._rem_inclusion('vis_rem_rel_path')
            md_div.append(  vis_rem )

        md_div.extend((     *extra_tokens,
                            '</div>\n\n',
                      ))    # The extra linefeed is there to enforce rendering of next md sections

        # Add extra indentation according to IDE's insertion:
        if self.indentation:
            md_div = [ s and self.indentation + s for s in md_div ]

        # Join every item with extra gaps, to following md rendering requirements
        out = '\n\n'.join(md_div)
        return out


    def _rem_inclusion(self, rem_path_kind:str):
        path_str = str(getattr(self.files_data, rem_path_kind))
        rem_uri  = to_uri( convert_url_to_utf8(path_str) )
        return f'--8<-- "{ rem_uri }"'



    def generate_buttons_row(self) -> str:
        """
        Build all buttons below an "ide" (editor+terminal).
        """
        buttons = [
            self.create_button("play"),
            self.create_button("check", btn_kind="validate") if self.has_check_btn else "",
            self.create_button("download", margin_left=1 ),
            self.create_button("upload", margin_right=1 ),
            self.create_button("restart"),
            self.create_button("save"),
        ]

        # Redactors only:
        if self.env.in_serve:
            if self.has_corr:
                buttons += (
                    self.create_button("corr_btn", margin_left=1),
                    self.create_button("show")
                )
            elif self.has_any_corr_rems:
                buttons += (
                    self.create_button("show", margin_left=1),
                )

        buttons      = ''.join(buttons)
        cnt_txt      = self.env.lang.attempts_left.msg
        cnt_txt_span = Html.span(cnt_txt + " : ", kls=HtmlClass.compteur_txt)
        cnt_or_inf   = self.max_attempts_symbol
        cnt_n_span   = Html.span(cnt_or_inf, id=f'{ Prefix.compteur_ }{ self.editor_name }')
        compteur     = Html.div(f"{ cnt_txt_span }{ cnt_n_span }/{ cnt_or_inf }", kls=HtmlClass.compteur)

        buttons_div  = Html.div(
            Html.div(buttons, kls=HtmlClass.ide_buttons_div)
            + Html.div(compteur, kls=HtmlClass.compteur_wrapper),
            kls = HtmlClass.ide_buttons_div_wrapper
        )
        return buttons_div
