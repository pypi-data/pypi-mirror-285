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

from ...messages import Lang
from ...tools_and_constants import HtmlClass, IdeMode
from .args_macros_classes import ArgConfig, ArgConfigNotIde, MacroConfig, VAR_ARGS




PY_GLOBAL = MacroConfig(
    '',
    ArgConfig(
        'py_name', str, default="", index=0,
        docs = "Chemin relatif (sans l'extension du fichier) vers le fichier `{exo}.py` et les "
               "éventuels autres fichiers annexes, sur lesquels baser l'IDE.",
    ),
    ArgConfig(
        'ID', int, in_config=False, docs_type="None|int",
        docs="À utiliser pour différencier deux IDEs utilisant les mêmes fichiers [{{annexes()}}]"
             "(--ide-files), afin de différencier leurs sauvegardes (nota: $ID \\ge 0$)."
    ),
    ArgConfig(
        'SANS', str, default="",
        docs = "Pour interdire des fonctions builtins, des méthodes ou des modules : chaîne de "
               "noms séparés par des virgules et/ou espaces."
    ),
    ArgConfig(
        'WHITE', str, default="",
        docs = "(_\"White list\"_) Ensemble de noms de modules/packages à pré-importer avant que "
               "les interdictions ne soient mises en place (voir argument `SANS` ; `WHITE` _est "
               "normalement {{ orange('**obsolète**') }}_)."
    ),
    ArgConfig(
        'REC_LIMIT', int, default=-1,
        docs = "Pour imposer une profondeur de récursion maximale. Nota: ne jamais descendre en-"
               "dessous de 20. La valeur par défaut, `#!py -1`, signifie que l'argument n'est pas "
               "utilisé."
    ),
    ArgConfig(
        'MERMAID', bool, default=False,
        docs = "Signale qu'un rendu de graphe mermaid sera attendu à un moment ou un autre des "
               "exécutions."
    ),
)




MOST_LIKELY_USELESS_ID = PY_GLOBAL.ID.copy_with(
    docs="À utiliser pour différencier deux appels de macros différents, dans le cas où vous "
         "tomberiez sur une collision d'id (très improbable, car des hachages sont utilisés. "
         "Cet argument ne devrait normalement pas être nécessaire pour cette macro)."
)

def _py_globals_copy_gen(**replacements:ArgConfig):
    return (
        (arg if name not in replacements else replacements[name]).copy_with()
        for name,arg in PY_GLOBAL.args.items()
    )





#----------------------------------------------------------------------------------------




BS_MACRO = '" + back_slash() + "'
# Pretty well named... XD
# Necessary to bypass the jinja deprecation warning when using backslashes where it doesn't like it...


IDE = MacroConfig(
    'IDE',
    *PY_GLOBAL.args.values(),
    ArgConfig(
        'MAX', int, default=5, docs_type="int|'+'",
        deprecated_source = 'ides.max_attempts_before_corr_available',
        docs = "Nombre maximal d'essais de validation avant de rendre la correction et/ou les "
               "remarques disponibles."
    ),
    ArgConfig(
        'LOGS', bool, default=True,
        deprecated_source = 'ides.show_assertion_code_on_failed_test',
        docs = "{{ red('Durant des tests de validation') }}, si LOGS est `True`, le code "
               "complet d'une assertion est utilisé comme message d'erreur, quand "
               "l'assertion a été écrite sans message."
    ),
    ArgConfig(
        'MAX_SIZE', int, default=30,
        deprecated_source = 'ides.default_ide_height_lines',
        docs = "Impose la hauteur maximale possible pour un éditeur, en nombres de lignes."
    ),
    ArgConfig(
        'TERM_H', int, default=10,
        deprecated_source = 'ides.default_height_ide_term',
        docs = "Impose le nombre de lignes du terminal."
    ),
    ArgConfig(
        'MODE', str, is_optional=True, docs_type='None|str', docs_default_as_type=True, line_feed_link=False,
        conf_type = C.Choice((IdeMode.no_reveal, IdeMode.no_valid)),
        docs = "Change le mode d'exécution des codes python. Les modes disponibles sont :<br>"
               "{{ul_li(["
                    f"\"`#!py None` : exécutions normales.\", "
                    f"\"`#!py {IdeMode.no_reveal!r}` : exécutions normales, mais les solutions et remarques, si elles existent, ne sont jamais révélées, même en cas de succès. Le compteur d'essais est ${ BS_MACRO }infty$.\", "
                    f"\"`#!py {IdeMode.no_valid!r}` : quels que soient les fichiers/sections disponibles, le bouton et les raccourcis de validations sont inactifs. Le compteur d'essais est ${ BS_MACRO }infty$.\", "
               "])}}"
    ),
)






TERMINAL = MacroConfig(
    'terminal',
    *_py_globals_copy_gen(
        ID = MOST_LIKELY_USELESS_ID,
        py_name = PY_GLOBAL.py_name.copy_with(
            docs = "Crée un terminal isolé utilisant le fichier python correspondant (sections "
                   "autorisées: `env`, `env_term`, `post_term`, `post` et `ignore`)."
        )
    ),
    ArgConfig(
        'TERM_H', int, default=10,
        deprecated_source = 'ides.default_height_isolated_term',
        docs = "Impose le nombre de lignes du terminal."
    ),
    ArgConfig(
        'FILL', str, default='', ide_link=False,
        docs = "Commande à afficher dans le terminal lors de sa création.<br>{{red('Uniquement "
               "pour les terminaux isolés.')}}"
    ),
)






PY_BTN = MacroConfig(
    'py_btn',
    *(
        arg.copy_with(in_docs=arg.name in ('py_name', 'ID', 'MERMAID'))
        for arg in _py_globals_copy_gen(
            ID = MOST_LIKELY_USELESS_ID,
            py_name = PY_GLOBAL.py_name.copy_with(
                docs="Crée un bouton isolé utilisant le fichier python correspondant (uniquement "
                    "`env` et `ignore`)."
            )
        )
    ),
    ArgConfigNotIde(
        'WRAPPER', str, default='div',
        docs = "Type de balise dans laquelle mettre le bouton."
    ),
    ArgConfigNotIde(
        'HEIGHT', int, is_optional=True, docs_type="None|int",
        docs = "Hauteur par défaut du bouton."
    ),
    ArgConfigNotIde(
        'WIDTH', int, is_optional=True, docs_type="None|int",
        docs = "Largeur par défaut du bouton."
    ),
    ArgConfigNotIde(
        'SIZE', int, is_optional=True, docs_type="None|int",
        docs = "Si défini, utilisé pour la largeur __et__ la hauteur du bouton."
    ),
    ArgConfigNotIde(
        'ICON', str, default="",
        docs = "Par défaut, le bouton \"play\" des tests publics des IDE est utilisé."
               "<br>Peut également être une icône `mkdocs-material`, une adresse vers une image "
               "(lien ou fichier), ou du code html.<br>Si un fichier est utiliser, l'adresse doit "
               "être relative au `docs_dir` du site construit."
    ),
    ArgConfigNotIde(
        'TIP', str, default=Lang.py_btn.msg,
        docs = "Message à utiliser pour l'info-bulle."
    ),
    ArgConfigNotIde(
        'TIP_SHIFT', int, default=50,
        docs = "Décalage horizontal de l'info-bulle par rapport au bouton, en `%` (50% correspond "
        "à un centrage)."
    ),
    ArgConfigNotIde(
        'TIP_WIDTH', float, default=0.0,
        docs = "Largeur de l'info-bulle, en `em` (`#!py 0` correspond à une largeur automatique)."
    ),
)






SECTION = MacroConfig(
    'section',

    # Required on the python side, but should never be given through "meta", so it has to be
    # non blocking on the config side:
    PY_GLOBAL.py_name.copy_with(
        docs="[Fichier python {{ annexe() }}](--ide-files).",
    ),
    ArgConfigNotIde(
        'section', str, index=1, is_optional=True,
        docs = "Nom de la section à extraire."
    ),
)






PY = MacroConfig(
    'py',

    # Required on the python side, but should never be given through "meta", so it has to be
    # non blocking on the config side:
    ArgConfigNotIde(
        'py_name', str, is_optional=True, index=0,
        docs = "Fichier source à utiliser (sans l'extension)."
    ),
)






MULTI_QCM = MacroConfig(
    'multi_qcm',

    # Required on the python side, but should never be given through "meta": must not be blocking:
    ArgConfigNotIde(
        '*inputs', list, index=VAR_ARGS, in_config=False, docs_default_as_type=False,
        docs = "Chaque argument individuel est une [liste décrivant une question avec ses choix "
               "et réponses](--qcm_question)."
    ),
    ArgConfigNotIde(
        'description', str, default='',
        docs = "Texte d'introduction (markdown) d'un QCM, ajouté au début de l'admonition, avant "
               "la première question. Cet argument est optionnel"
    ),
    ArgConfigNotIde(
        'hide', bool, default=False,
        docs = "Si `#!py True`, un masque apparaît au-dessus des boutons pour signaler à "
               "l'utilisateur que les réponses resteront cachées après validation."
    ),
    ArgConfigNotIde(
        'multi', bool, default=False,
        docs = "Réglage pour toutes les questions du qcms ayant à ou un seul choix comme bonne "
               "réponse, indiquant si elles sont à choix simples ou multiples."
    ),
    ArgConfigNotIde(
        'shuffle', bool, default=False,
        docs = "Mélange les questions et leurs choix ou pas, à chaque fois que le qcm est joué."
    ),
    ArgConfigNotIde(
        'shuffle_questions', bool, default=False,
        docs = "Change l'ordre des questions uniquement, à chaque fois que le qcm est joué."
    ),
    ArgConfigNotIde(
        'shuffle_items', bool, default=False,
        docs = "Mélange seulement les items des questions, à chaque fois que le qcm est joué."
    ),
    ArgConfigNotIde(
        'admo_kind', str, default="!!!",
        docs = "Type d'admonition dans laquelle les questions seront rassemblées (`'???'` et "
               "`'???+'` sont également utilisables, pour des qcms repliés ou \"dépliés\")."
    ),
    ArgConfigNotIde(
        'admo_class', str, default="tip",
        docs ="Pour changer la classe d'admonition. Il est également possible d'ajouter d'autres "
              "classes si besoin, en les séparant par des espaces (ex: `#!py 'warning my-class'`)."
    ),
    ArgConfigNotIde(
        'qcm_title', str, default=Lang.qcm_title.msg,
        docs = "Pour changer le titre de l'admonition."
    ),
    ArgConfigNotIde(
        'DEBUG', bool, default=False,
        docs = "Si True, affiche dans la console le code markdown généré pour ce qcm."
    ),
)



FIGURE = MacroConfig(
    'figure',

    # Required on the python side, but should never be given through "meta": must not be blocking:
    ArgConfigNotIde(
        'div_id', str, default="figure1", index=0,
        docs = "Id html de la div qui accueillera la figure dessinée avec matplotlib."
               "<br>À modifier s'il y a plusieurs figures insérées dans la même page."
    ),
    ArgConfigNotIde(
        'div_class', str, default=HtmlClass.py_mk_figure,
        docs = "Classe html à donner à la div qui accueillera la figure.<br>Il est possible d'en "
               "changer ou d'en mettre plusieurs, selon les besoins. Il est aussi possible de "
               "surcharger les règles css de la classe par défaut, pour obtenir l'affichage voulu."
    ),
    ArgConfigNotIde(
        'inner_text', str, default=Lang.figure_text.msg,
        docs = "Texte qui sera affiché avant qu'une figure ne soit tracée."
    ),
    ArgConfigNotIde(
        'admo_kind', str, default="!!!",
        docs = "Type d'admonition dans laquelle la figure sera affichée (`'???'` et `'???+'` "
               "sont également utilisables, pour des qcms repliés ou \"dépliés\")."
               "<br>Si `admo_kind` est `''`, la `<div>` sera ajoutée sans admonition (et les "
               "arguments suivants seront alors ignorés)."
    ),
    ArgConfigNotIde(
        'admo_class', str, default="tip",
        docs ="Pour changer la classe d'admonition. Il est également possible d'ajouter d'autres "
              "classes si besoin, en les séparant par des espaces (ex: `#!py 'warning my-class'`)."
    ),
    ArgConfigNotIde(
        'admo_title', str, default=Lang.figure_admo_title.msg,
        docs = "Pour changer le titre de l'admonition."
    ),
)






ARGS_MACRO_CONFIG = MacroConfig.build_config_and_accessors(
    'args',
    IDE,
    TERMINAL,
    PY_BTN,
    SECTION,
    MULTI_QCM,
    PY,
    FIGURE,
)
