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

import re
from functools import wraps
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple

from mkdocs.exceptions import BuildError

from ..pyodide_logger import logger
from ..plugin.maestro_extras import MaestroExtras
from ..tools_and_constants import MACROS_WITH_INDENTS, HtmlClass, Kinds, ScriptKind









FIX_P = '</p KEEP>'



def multi_qcm(env:MaestroExtras):
    """
    @inputs:          lists of data for one question, aka:
                        - question title
                        - list of choices
                        - list of correct answers
                        - kwargs, for single=Optional[bool]  >>>  spec not fixed yet...
    @shuffle=False:   Questions and their items are shuffled on each refresh/retry
    @hide=False:      Correct answers will stay hidden if True after checking the user's answers
    @multi=None:      Set the default behavior for unique correct answers, at qcm level.
    @admo_kind="!!!": Control the kind of admonition used for the QCM
    @admo_type='tip': Category of admonition to use
    @qcm_title=None:  Title for the admonition. If not given "Question" (possibly plural) is used.

    @DEBUG=False:     If True, md output will be printed to the console
    """

    MACROS_WITH_INDENTS.add('multi_qcm')

    @wraps(multi_qcm)
    def wrapped(
        *inputs,
        # REMINDER: _NOTHING_ should ever be left to None at runtime (MaestroMeta)
        description:str=None,
        hide:       bool=None,
        multi:      bool=None,
        shuffle:    bool=None,
        shuffle_questions: bool=None,
        shuffle_items: bool=None,
        admo_kind:  str =None,
        admo_class: str =None,
        qcm_title:  str =None,
        DEBUG:      bool=None,
        ID=None,                        # sink (deprecated)
    ):
        """
        WARNING:    Extra closing </p> tags needed here and there to guarantee the final
                    html structure!

        Reasons:
        1. THE MD RENDERER GENERATES INVALID HTML, WHEN MIXING html+md PERIOD!
        2. The md renderer will automatically open a <p> tag when starting the admo content
        3. If _ever_ the user defines a multiline content anywhere in the qcm, a new <p>
            tag will be started, leaving the previous one hanging in the air...
        So far, so good...: the html is invalid, but rendered correctly/usable in a browser.
        4. CATACLYSM: use another plugin that will pass that html to the BSoup...:
            Depending on the html parser used, Beautif(o)ulSoup _WILL_ generate the missing
            closing tags, and this will entirely mess up the rendered page.

        So, to avoid this, the extra closing `</p>` are added. They _LOOK_ like they are hanging,
        but they _will_ actually produce valid html!
        """

        env.set_current_page_insertion_needs(Kinds.qcm)


        def qcm_start():
            nonlocal qcm_title
            qcm_id       = env.get_qcm_id()
            shuffled     = shuffle or shuffle_questions
            admo_classes = ' '.join(filter(bool,(
                HtmlClass.py_mk_admonition_qcm,
                HtmlClass.qcm_shuffle * shuffled,
                HtmlClass.qcm_hidden * hide,
                HtmlClass.qcm_multi if multi else HtmlClass.qcm_single,
                qcm_id,
            )))

            # If using default, pick plural when appropriate:
            if qcm_title == env.lang.qcm_title.msg:
                qcm_title = env.lang.qcm_title.one_or_many( len(questions_data) > 1 )
            admo_qcm = f'{ indent }{ admo_kind } { admo_class } { admo_classes } "{ qcm_title }"'
            return [
                admo_qcm,
                '',         # ALWAYS KEEP THIS!
                *(
                    () if not description else (auto_indent(qcm_format(description)), '')
                ),
                auto_indent(f'\n{ FIX_P }<ol class="{ HtmlClass.py_mk_question_qcm }">\n'),
            ]


        def qcm_close():
            admonition_lst.append(auto_indent(f"{ FIX_P }</ol>"))


        def question_open(question:str, n:int, lst_answers:List[int], default_multi, shuffled):
            is_multi  = len(lst_answers) > 1
            multi_kls = HtmlClass.qcm_multi if is_multi or default_multi else HtmlClass.qcm_single
            item_kls  = f'class="{ HtmlClass.py_mk_question_qcm } { multi_kls } { shuffled * HtmlClass.qcm_shuffle}"'
            answers   = ','.join( map(str, lst_answers) )
            tag_open  = f'{ FIX_P }<li { item_kls } correct="{ answers }" markdown>\n{ question }'

            admonition_lst.append(auto_indent(tag_open))


        def question_close():
            admonition_lst.append(auto_indent("</li>\n"))
            # Extra linefeed for presentational purpose only


        def question_options(items):
            """ Always use "md_in_html" approach, to simplify the construction. It is required
                anyway when the first item starts with a code block...
            """
            admonition_lst.append(
                auto_indent(f'{ FIX_P }<ul class="{ HtmlClass.py_mk_item_qcm }">')
            )
            admonition_lst.extend(
                auto_indent(item, wrap_li=True) for item in items
            )
            admonition_lst.append(
                auto_indent("</ul>")
            )



        def validate_question_config(n_question, question, items, lst_correct, multi):

            duplicates = len(lst_correct) != len(set(lst_correct))
            unknown    = set(lst_correct) - set(range(1,1+len(items)))

            msg = ""
            if duplicates:
                msg = f"Correct answers contain duplicated values: {lst_correct}"

            elif unknown:
                msg = f"Correct answers contain invalid items number: {unknown}"
                if 0 in unknown:
                    msg += "\n(Note: correct answers are not given as indices and start with 1)"

            elif not lst_correct and (not multi or env.forbid_no_correct_answers_with_multi):
                msg = (
                    "This question is declared as \"single choice\" but has no correct "
                    "answer specified:\n"
                    "* Either specify a correct answer,\n"
                    "* Or set `multi` to True one way or another:"
                    "\n    - question's array 4th element (optional dict),"
                    "\n    - multi_qcm macro argument,"
                    "\n    - page headers,"
                    "\n    - meta files,"
                    "\n    - plugins's config in mkdocs.yml)."
                )

            if msg:
                msg = (
                    f"\nIn file { env.file_location() }\nIn the QCM titled: { qcm_title !r}"
                    f"\nQuestion {n_question}:\n{ question !r}"
                    f"\n\n{msg}"
                )
                if env._dev_mode:
                    logger.error('QCMs - EXPECTED (x1)\n'+msg)
                else:
                    raise BuildError(msg)


        #------------------------------------------------------------------


        if len(inputs)==1 and isinstance(inputs[0], str):
            inputs = extract_csv_file(env, inputs[0])

        # Unify data, adding/extracting systematically the extra_dct element:
        questions_data: List[ Tuple[str, list, List[int], Dict[str,Any]] ] = [
            [
                qcm_format(q),
                [*map(qcm_format,items)],
                sorted(ans),
                dct[0] if dct else {}
            ]
            for q, items, ans, *dct in inputs
        ]

        indent      = env.get_macro_indent()
        auto_indent = auto_indenter_factory(indent)

        admonition_lst = qcm_start()
        for n, (question, items, lst_answers, extra_dct) in enumerate(questions_data, 1):

            shuffled = extra_dct.get('shuffle', shuffle or shuffle_items)
            is_multi = extra_dct.get('multi',   multi)
            validate_question_config(n, question, items, lst_answers, is_multi)

            question_open(question, n, lst_answers, is_multi, shuffled)
            question_options(items)
            question_close()
        qcm_close()


        output = '\n'.join(admonition_lst)
        output = f'\n\n{ output }\n\n'    # Enforce empty spaces around in the markdown admonition

        if DEBUG:
            # The user doesn't need to know about the CORRECT_CLOSE_P thing, so remove them first:
            to_print = output.replace(FIX_P, '')
            print('\vCall to multi_qcm in page', env.page.file.src_uri, '\n', to_print)
        return output

    return wrapped








def auto_indenter_factory(indent:str):
    """ Auto-indenter factory """

    indent += '    '

    def indenter(content:str, wrap_li=False, lvl:int=1):
        """
        Takes a @content, possibly multiline, and indent all lines (including the first) with the
        base @indent and an extra @lvl, where each level counts for 4 space characters.

        If @wrap_li is True, handle the "li" element appropriately, meaning:
            - prepend with "* " for simple content
            - surround the item with `<li markdown>...</li> if it's a code bloc`
        """
        if wrap_li:
            content = f'<li class="{ HtmlClass.py_mk_item_qcm }" markdown="1">\n{ content }\n</li>'
        return indent + content.replace('\n',"\n"+indent)

    return indenter




def qcm_format(msg:str):
    """ Use the natural/minimal indentation and strip spaces on both ends """
    bare = dedent(msg).strip()
    return f"{ bare }\n"





#---------------------------------------------------------------------------------



QUOTES = "'‘“\""


def extract_csv_file(env:MaestroExtras, input_file, sep=";") -> List[str] :
    """ Extract info from external file, to build a multi qcm """

    env.warn_unmaintained('The macro `multi_qcm` using the csv data extraction')

    def csv_entry_to_qcm_input(entry:dict):
        question = entry["Question"]
        list_answers = [entry[key] for key in entry if "Answer" in key and entry[key] is not None]
        list_correct = list(map(int, entry["Valid"].split(",")))
        dictionnaire_var = to_dict(entry["Variable"]) if entry["Variable"] is not None else None
        return [question, list_answers, list_correct, dictionnaire_var]

    def to_dict(string:str):
        string = string + ","
        dico = {}
        regex = r"\s*(\w*)\s*:\s*(\[[\s\w,\.'\"‘“’”]*\]|\w*)\s*,"
        words: List[str] = re.findall(regex, string)
        for var in words:
            dico[var[0]] = list(map(convert_type, var[1].strip("[").strip("]").split(",")))
        return dico

    def convert_type(string:str):
        string = string.strip()
        if string[0] in QUOTES:
            return str(string[1:-1])
        elif "." in string:
            return float(string)
        else:
            return int(string)

    #------------------------------------------------------------------

    cvs_target = env.get_sibling_of_current_page(input_file)     # NON TESTÉ

    if not cvs_target or not cvs_target.is_file():
        return []

    csv_file = []
    file_content = cvs_target.read_text(encoding="utf-8")
    content = file_content.splitlines()
    header = content.pop(0).split(sep)
    for ligne in content:
        split_ligne = ligne.split(sep)
        dico = {
            header[i]: split_ligne[i].replace("\\\\", "\\") if split_ligne[i] != "" else None
            for i in range(len(header))
        }
        csv_file.append(dico)

    inputs = tuple(map(csv_entry_to_qcm_input, csv_file))
    return inputs
