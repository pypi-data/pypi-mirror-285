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

# pylint: disable=all

from typing import Any, Dict, Optional, TYPE_CHECKING

from pyodide_mkdocs_theme.pyodide_macros.tools_and_constants import HtmlClass

if TYPE_CHECKING:
    from ..plugin.pyodide_macros_plugin import PyodideMacrosPlugin





def html_builder_factory(template:str, allow_content):
    def tagger(tag:str, **props):
        def html_builder(
            content:str="",
            *,
            id:str='', kls:str="", attrs: Dict[str, str]=None,
            **kwargs
        ) -> str:
            """
            Build a the code for the given tag element.
            The id and kls named arguments, and also all keyword arguments have precedence over the
            content of the attrs dict. This dict allow to define hyphen separated attributes (like
            "data-max_size" and so on).

            NOTE: Using the @content argument on "mono tags" will raise ValueError.
            """
            if not allow_content and content:
                raise ValueError(f"Cannot use content on {tag!r} tags ({content=!r})")

            attrs = attrs or {}
            attrs.update(props)
            attrs.update(kwargs)
            if id:  attrs['id'] = id
            if kls: attrs['class'] = kls

            attributes = " ".join(
                f'{ name }="{ value }"' #if name!='onclick' else f'{ name }={ value }'
                for name,value in attrs.items()
            )
            code = template.format(tag=tag, content=content, attributes=attributes)
            return code

        return html_builder
    return tagger



mono_tag = html_builder_factory("<{tag} {attributes} />", False)
bi_tag   = html_builder_factory("<{tag} {attributes}>{content}</{tag}>", True)




input   = mono_tag('input')
img     = mono_tag('img')

a       = bi_tag('a')
button  = bi_tag('button', type='button') # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#notes
code    = bi_tag('code')
div     = bi_tag('div')
script  = bi_tag('script')
span    = bi_tag('span')
svg     = bi_tag('svg')




def tooltip(txt:str, width_em:Optional[int]=None, shift:int=50):
    """
    Generic CodEx tooltip builder. If width_em is falsy, use automatic width.
    Th @shift argument is the % to use for the translation, 0% means the tooltip will got on the
    right, 100% means it will go on the left. With 50 (default), it's centered below the original element
    """
    dct = {
        'kls': 'tooltiptext',
        'style': f'--tool_shift: {shift}%;',
    }
    if width_em:
        dct['style'] += f"width:{ width_em }em;"

    return span(txt, **dct)





def terminal(term_id:str, kls:str, n_lines_h:int, env:'PyodideMacrosPlugin', **kw):
    """
    Build a terminal div with its button. If n_lines_h is falsy, the height of the div isn't
    handled. Otherwise, it's the mac of n_lines_h and 5.
    """
    n_buttons = 0
    shift = 97

    # Build buttons:
    tip = tooltip(env.lang.feedback, width_em=env.lang.feedback.em, shift=shift)
    feed_div = div(
        _BTN_STDOUT_SVG + tip,
        kls = f"twemoji { HtmlClass.stdout_ctrl } { HtmlClass.tooltip }"
    )
    n_buttons += 1

    tip_wrap = tooltip(env.lang.wrap_term, width_em=env.lang.wrap_term.em, shift=shift)
    wrap_div = div(
        _BTN_MATERIAL_OVERFLOW + tip_wrap,
        kls=f"{ HtmlClass.stdout_wrap_btn } {HtmlClass.tooltip }",
        style="--wrap-opacity: 30%",
    )
    n_buttons += 1

    # Group buttons:
    btns_div = div(
        feed_div + wrap_div,
        kls=f"{ HtmlClass.term_btns_wrapper }",
    )

    # Build main div:
    if n_lines_h:
        n_lines_h = max(n_lines_h, 5)
        kw['style'] = f"--n-lines:{ n_lines_h };" + kw.get('style','')
    kw['style'] = 'line-height:24px;' + kw.get('style','')

    term_div = div(id=term_id, kls=f"{kls} { HtmlClass.py_mk_terminal }", **kw)

    global_div = div(
        term_div+btns_div,
        kls=HtmlClass.term_wrapper,
        style=f'--n-buttons:{ n_buttons }'
    )
    return global_div


_BTN_STDOUT_SVG = '''
<svg viewBox="0 0 24 24" fill="none"
    stroke="var(--md-default-fg-color)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"
    xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
<g>
  <path d="M 4,21.4 V 2.6 C 4,2.3 4.3,2 4.6,2 h 11.65 c 0.16,0 0.31,0.06 0.42,0.18 l 3.15,3.15 C 19.94,5.44 20,5.59 20,5.75 V 21.4 C 20,21.73 19.73,22 19.4,22 H 4.6 C 4.3,22 4,21.73 4,21.4 Z" ></path>
  <path d="M 16,5.4 V 2.35 C 16,2.16 16.16,2 16.35,2 c 0.09,0 0.18,0.03 0.25,0.10 l 3.29,3.29 C 19.96,5.46 20,5.55 20,5.65 20,5.84 19.84,6 19.65,6 H 16.6 C 16.27,6 16,5.73 16,5.4 Z" ></path>
  <path d="m 8,9.25 h 8" ></path>
  <path d="M 7.9,13.25 H 15.9"></path>
  <path d="M 7.9,11.25 H 14.4" ></path>
  <path d="M 7.9,19.25 H 14.4" ></path>
  <path d="m 7.9,15.25 h 8" ></path>
  <path d="M 7.9,17.25 H 11.9" ></path>
  <path d="m 8,5.25 h 4" ></path>
  <path d="m 8,7.25 h 4" ></path>
</g>
<g><path class="stdout-x-ray-svg" d="M 3,11.4 v 6 L 21,13.8 V 7.7 Z" style="fill:var(--md-default-bg-color);stroke-width:0;" ></path></g>
</svg>
'''.replace('\n',' ')       # needed otherwise insertion in admonitions fails... XD


# Cannot use the `:material-overflow:` syntax, because not rendered when the terminal is not
# inside an admonition or tab... DX (markdown attributes missing, but putting them in IDE makes a whole mess of them...)
_BTN_MATERIAL_OVERFLOW = '''
<span class="twemoji">
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<path d="M7 21H5V3h2v18m7-18h-2v6h2V3m0 12h-2v6h2v-6m5-3-3-3v2H9v2h7v2l3-3Z">
</path></svg></span>'''.replace('\n',' ')       # needed otherwise insertion in admonitions fails... XD
