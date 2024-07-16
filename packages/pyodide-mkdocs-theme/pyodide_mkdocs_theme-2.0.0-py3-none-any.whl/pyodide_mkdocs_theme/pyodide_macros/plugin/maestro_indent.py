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


import re
from typing import Callable, List, Optional, Tuple


from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.exceptions import BuildError


from ..exceptions import (
    PyodideConfigurationError,
    PyodideMacrosParsingError,
    PyodideMacrosTabulationError,
    PyodideMacrosIndentError,
)
from ..tools_and_constants import MACROS_WITH_INDENTS
from ..pyodide_logger import logger
from .maestro_base import BaseMaestro
from .maestro_meta import MaestroMeta




# pylint: disable-next=pointless-string-statement, line-too-long
'''
- Macros are run in "reading order" of the original document, included content also being used
  this way => fully predictable
- WARNING with md_include, which interleaves other calls in the "current context"... => needs
  an external md page parser
- Process:
    1. remove raw markers. NOTE: nested raw markups aren't allowed => easy
    2. tokenize (longest tokens first)
    3. _carefully parse the thing_, keeping in mind that the input is md text, not actual python...
       and store the indents of the calls to multiline macros in a reversed stack (store a pari
       indent/macro name, to enforce validity of executions on usage)
    4. each time a macro starts running (spotted through the custom macro decorator), pop the
       current indent to use, AND STACK IT, because of potential nested macro calls: A(BCD)
       => when going back to A, there is no way to know if the macro will reach for the
       indentation value of A, for example.
       Each time the macro returns, pop the current indent from the second stack
    5. for nested macro, add the included indentation data on top of the current reversed stack.
'''







class MaestroIndent(BaseMaestro):
    """ Manage Indentation logistic """

    _running_macro: Optional[str] = None
    """
    Name of the macro currently running (or the last one called. None if no macro called yet).
    """

    _parser: 'IndentParser'

    _indents_store: List[Tuple[str,int]]
    """ List of all indentations for the "macro with indents" calls throughout the page, in
        reading order (=dfs).
        Data are stored in reversed fashion, because consumed using `list.pop()`.
    """

    _indents_stack: List[str]
    """ Stack the current indentation level to use, the last element being the current one.
        This allows the use of macros through multi layered inclusions (see `md_include`),
        getting back the correct indentations when "stepping out" of the included content.
    """


    def on_config(self, config:MkDocsConfig):

        nope = [ w for w in self.macros_with_indents if not w.isidentifier() ]
        if nope:
            raise PyodideConfigurationError(
                "Invalid macros_with_indents option: should be a list of identifiers, but found: "
                f"{ ', '.join(map(repr,nope)) }"
            )

        self._parser = IndentParser(
            self.j2_block_start_string    or "{%",
            self.j2_block_end_string      or "%}",
            self.j2_variable_start_string or "{{",
            self.j2_variable_end_string   or "}}",
            self.is_macro_with_indent,
        )

        super().on_config(config)     # MacrosPlugin is actually "next in line" and has the method

        # after super call, the macro have been registered, so MACROS_WITH_INDENTS isn't empty anymore
        macros = [*MACROS_WITH_INDENTS] + self.macros_with_indents
        self._macro_with_indent_pattern = re.compile('|'.join(macros))



    def on_page_markdown(
        self,
        markdown:str,
        page:Page,
        config:MkDocsConfig,
        site_navigation=None,
        **kwargs
    ):

        file_loc     = self.file_location(page)
        indentations = self._parser.parse(markdown, file_loc, tab_to_spaces=self.tab_to_spaces)

        self._indents_store = [*reversed(indentations)]
        self._indents_stack = []

        out = super().on_page_markdown(
            markdown, page, config, site_navigation=site_navigation, **kwargs
        )

        if self._indents_store:
            content = ''.join( f"\n    {name}: {n}" for name,n in reversed(self._indents_store) )
            raise PyodideMacrosIndentError(
                "Registered macros calls with indents have not been entirely consumed for "
                f"{ file_loc }. The remaining store content is:{ content }"
            )
        if self._indents_stack:
            raise PyodideMacrosIndentError(
                "Indentations stack inconsistency when rendering the markdown page for "
                f"{ file_loc }. The remaining stack content is:\n    {self._indents_stack!r}"
            )
        return out



    #----------------------------------------------------------------------------



    def apply_macro(self, name, func, *a, **kw):
        """
        Gathers automatically the name of the macro currently running (for better error
        messages). Also validate the call config for macros with indents
        """
        self._running_macro = name
        need_indent = self.is_macro_with_indent(name)
        if need_indent:
            call,indent = self._indents_store.pop()
            if call != name:
                raise BuildError(
                    f"Invalid indentation data: expected a call to {call}, but was {name}"
                )
            self._indents_stack.append(indent * ' ')

        out = super().apply_macro(name, func, *a, **kw)

        if need_indent:
            self._indents_stack.pop()
        return out




    def is_macro_with_indent(self, macro_call:str) -> bool:
        """
        Return True if the given macro call requires to register indentation data.
        This is using a white list, so that user defined macro cannot cause troubles.
        """
        return bool(self._macro_with_indent_pattern.fullmatch(macro_call))


    def get_macro_indent(self):
        """
        Extract the indentation level for the current macro call.
        """
        if not self._indents_stack:
            raise BuildError(f"No indentation data available in page { self.file_location() }")
        return self._indents_stack[-1]

    def indent_macro(self, code:str):
        """ Automatically indent appropriately the given macro output markdown. """
        indent   = self.get_macro_indent()
        out_code = code.replace('\n', '\n'+indent)
        return out_code


    def get_indent_in_current_page(self, _:re.Pattern=None):
        """
        Extract the indentation needed for the given macro template call.
        @throws:    BuildError if the same macro call is found several times in the page.
        """
        self.warn_unmaintained(
            msg = "Deprecated usage of PyodideMacrosPlugin.get_indent_in_current_page.\n"
                  "The get_macro_indent method should be used instead."
        )
        return self.get_macro_indent()










class IndentParser:
    """
    Build a markdown parser class, extracting the indentations of macros calls requiring
    indentation, and taking in consideration jinja markups (skip {% raw %}...{% endraw %},
    properly parse complex macro calls, ignore macro variables).

    The result of the method `IndentParser(content).parse()` is a list of `Tuple[str,int]`:
    `(macro_name, indent)`, in the order they showed up in the content.
    """

    STR_DECLARATIONS = '"""', "'''", '"', "'"
    EXTRAS_TOKENS    = [r'\w+', r'\n', r'[\t ]+', r'\\', '.']

    __CACHE = {}

    def __init__(self,
        open_block:str,
        close_block:str,
        open_var:str,
        close_var:str,
        is_macro_with_indent:Callable[[str],bool],
    ):
        self.is_macro_with_indent = is_macro_with_indent

        # Build the delimiters according to the user config of the MacrosPlugin:
        self.open_block  = open_block
        self.close_block = close_block
        self.open_var    = open_var
        self.close_var   = close_var
        self.open_raw    = f'{open_block} raw {close_block}'
        self.close_raw   = f'{open_block} endraw {close_block}'
        self.pairs       = {}

        # Defined in self.parse(...):
        self.src_file = None
        self.tab_to_spaces = -1
        self.i        = 0
        self.tokens   = []
        self.indents  = []
        self.current  = None        # current macro call


        raw_open_close = [
            [self.open_raw, self.close_raw],
            [open_block,    close_block],
            [open_var,      close_var],
            *( [s,s] for s in self.STR_DECLARATIONS),
            ['(', ')'],
            ['[', ']'],
            ['{', '}'],
        ]
        tokens = []
        for o,c in raw_open_close:
            self.pairs[o] = c
            tokens += [o,c]

        tokens.sort(key=len, reverse=True)

        self.pattern = re.compile('|'.join(
            [re.escape(s).replace('\\ ',r'\s*') for s in tokens] + self.EXTRAS_TOKENS
        ), flags=re.DOTALL)



    def parse(self, content:str, src_file=None, *, tab_to_spaces=-1):
        """
        Parse the given content and extract all the indentation levels for each macro call
        identified as being a "macro_with_indent".

        - Returns a copy of the result.
        - Results are cached in between builds.
        """
        # pylint: disable=attribute-defined-outside-init
        self.src_file = src_file
        self.tab_to_spaces = tab_to_spaces

        if content not in self.__CACHE:
            self.i = 0
            self.tokens = self.pattern.findall(content)
            self.indents = []

            while self.i < len(self.tokens):
                tok = self._eat()
                if   tok == self.open_var:     self._gather_jinja_var()             # pylint: disable=multiple-statements
                elif tok == self.open_raw:     self._eat_until(self.close_raw)      # pylint: disable=multiple-statements
                elif tok == self.open_block:   self._eat_until(self.close_block)    # pylint: disable=multiple-statements

            self.__CACHE[content] = self.indents

        return self.__CACHE[content][:]


    #-------------------------------------------------------------
    #                       Error feedback
    #-------------------------------------------------------------


    def __extract(self, i_src, di):
        i,j = (i_src+di, i_src) if di<0 else  (i_src+1, i_src+1+di)

        # Enforce " is always used (otherwise, might end up with ' on one side and " on the other)
        a,b = ('"', '') if di<0 else ('', '"')
        rpr = repr(''.join(self.tokens[i:j]))[1:-1].replace('"','\\"')
        out = a + rpr + b

        return out


    def __location_info(self, tok, i:Optional[int]=None):
        i = self.i if i is None else i
        return f"{ self.__extract(i,-10) }\033[31m>>{tok}<<\033[0m{ self.__extract(i,10) }"


    def _error_info(self, info:str, tok:str):
        macro = ''
        indents = "No indents found so far."

        if self.current:
            i,msg = self.current
            macro = (
                f"\nMacro being parsed during the error (index : { i }/{ len(self.tokens) }):\n"
                f"    { msg }\n"
            )
        if self.indents:
            indents = "\nKnown indents so far: " + ''.join(
                f"\n\t{name}: {n}" for name,n in self.indents
            )

        return (
            "Parsing error while looking for macro calls indentation data.\n"
            "The parser might EOF when strings in a macro call are improperly written, so double "
            "check there are no unescaped delimiters inside strings used in the macro call.\n"
            f"With \033[31m>>tok<<\033[0m denoting the tokens of interest:\n\n"
            f"\033[34m{ info }, in { self.src_file }\033[0m\n{ macro }\n"
            f"Tokens around the error location (index: { self.i }/{ len(self.tokens) }):\n"
            f"    { self.__location_info(tok) }\n"
            f"\n{ indents }"
        )


    #-------------------------------------------------------------
    #                     Parsing machinery
    #-------------------------------------------------------------


    def _taste(self) -> Optional[str] :
        return self.tokens[self.i] if self.i<len(self.tokens) else None

    def _eat(self,reg:str=None, msg:str=None):
        tok = self._taste()
        if tok is None or reg is not None and not re.fullmatch(reg, tok):
            tok = 'EOF' if tok is None else repr(tok)
            reg = reg or msg
            msg = 'Reached EOF' if not reg else f'Expected pattern was: {reg!r}, but found: {tok}'
            raise PyodideMacrosParsingError( self._error_info(msg, tok) )
        self.i+=1
        return tok

    def _walk(self):
        while True:
            tok = self._taste()
            if not tok or not tok.isspace(): return                 # pylint: disable=multiple-statements
            self.i += 1

    def _eat_until(self, target, apply_backslash=False):
        while True:
            tok = self._eat(msg=target)
            if tok==target:
                return
            elif tok=='\\' and apply_backslash: self._eat()         # pylint: disable=multiple-statements



    def _consume_code(self, target:str):
        while True:
            tok = self._eat(msg=target)
            if tok==target:
                break
            elif tok in self.pairs:
                is_str_declaration = tok in self.STR_DECLARATIONS
                closing = self.pairs[tok]
                if is_str_declaration:
                    self._eat_until(closing, True)
                else:
                    self._consume_code(closing)


    def _gather_jinja_var(self):
        start = self.i-1        # index of the '{{' token, to compute indentation later
        self._walk()
        i_name = self.i
        name = self._eat(r'\w+')
        self._walk()
        tok = self._taste()
        is_macro = tok=='('

        self.current = i_name, self.__location_info(name, i_name)
        if is_macro and self.is_macro_with_indent(name):
            self._store_macro_with_indent(start, name)
            self._eat()
            self._consume_code(')')

        self._consume_code(self.close_var)


    def _store_macro_with_indent(self, start:int, name:str):
        i = max(0, start-1)
        while i>0 and self.tokens[i].isspace() and self.tokens[i] != '\n':
            i -= 1

        tok = self.tokens[i]
        if i and tok not in ('\n',self.open_var):
            raise PyodideMacrosParsingError( self._error_info(
                f"Invalid macro call:\nThe {name!r} macro is a `macros_with_indents` "
                 "but a call to it has been found with characters on its left. This is "
                f"not possible.\nThis happened", tok)
            )

        i += tok=='\n'
        indent = ''.join(self.tokens[i:start])
        if '\t' in indent:
            if self.tab_to_spaces<0:
                raise PyodideMacrosTabulationError(
                    "A tabulation character has been found on the left of a multiline macro call."
                    "\nThis is considered invalid. Solutions:\n"
                    "    - Configure your IDE to automatically convert tabulations into spaces.\n"
                    "    - Replace them with spaces characters manually.\n"
                    "    - Or set the `build.tab_to_spaces: integer` option of the plugin (NOTE:"
                    " depending on how the macros calls have been written, this might not always"
                    " work).\n"
                    "      If done so, warnings will be shown in the console with the locations"
                    " of each of these updates, so that they can be checked and fixed."
                )
            else:
                indent = indent.replace('\t', ' '*self.tab_to_spaces)
                logger.warning(
                    f"Automatic conversion of tabs to spaces in { self.src_file }, for the macro "
                    f"call: { self.current[1] }"
                )
        n_indent = len(indent)
        self.indents.append( (name, n_indent) )

