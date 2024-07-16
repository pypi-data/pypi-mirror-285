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


from typing import ClassVar, Optional, Tuple, Union
from dataclasses import dataclass

from .. import html_builder as Html
from ..tools_and_constants import HtmlClass, Kinds, Prefix, ScriptKind
from ..parsing import items_comma_joiner
from ..pyodide_logger import logger
from .ide_manager import IdeManager





@dataclass
class Terminal(IdeManager):
    """
    Builds an isolated terminal, potentially associated with some python file(s).
    """

    ID_PREFIX: ClassVar[str] = Prefix.term_only_

    NEEDED_KINDS: ClassVar[Tuple[ScriptKind]] = Kinds.pyodide, Kinds.terms

    KW_TO_TRANSFER: ClassVar[Tuple[Tuple[str,str]]] = (
        ('SIZE',    'term_height'),
        ('TERM_H',  'term_height'),
        ('FILL',    'prefill_term'),
    )

    JS_EXPORTED_VALUES: ClassVar[Optional[set]] = set("""
        prefill_term
        stdout_cut_off
    """.split())


    def handle_extra_args(self):

        # Backward compatibility:
        if isinstance(self.py_name, int):
            logger.warning(
                f"Invalid macro argument in { self.env.file_location() }:\n"
                f"`{'{{'} terminal({ self.py_name }) {'}}'}` should be replaced with "
                f"`{'{{'} terminal(TERM_H={ self.py_name }) {'}}'}`"
            )
            self.py_name, self.term_height = '', self.py_name

        if 'FILL' not in self.extra_kw:
            self.extra_kw['FILL'] = ''

        super().handle_extra_args()


    def _validate_files_config(self, _: Union[int,float]):

        forbidden = [*filter(bool,(
            "user code"      * self.files_data.has_code,
            "public tests"   * self.files_data.has_tests,
            "secret tests"   * self.files_data.has_secrets,
            "a correction"   * self.has_corr,
            "a REM file"     * self.has_rem,
            "a VIS_REM file" * self.has_vis_rem,
        ))]
        if forbidden:
            items = items_comma_joiner(forbidden, 'and')
            msg   = f"No data should be provided in these sections:\n        {items}"
            super()._validation_outcome(msg)




    def make_element(self) -> str:
        """
        Create an IDE (Editor+Terminal+buttons) within an Mkdocs document. {py_name}.py
        is loaded in the editor if present.
        """
        terminal_div = Html.terminal(
            self.editor_name,
            kls = f'{HtmlClass.py_mk_wrapper} {HtmlClass.term_solo}',
            n_lines_h = self.term_height,
            env       = self.env,
        )
        return terminal_div
