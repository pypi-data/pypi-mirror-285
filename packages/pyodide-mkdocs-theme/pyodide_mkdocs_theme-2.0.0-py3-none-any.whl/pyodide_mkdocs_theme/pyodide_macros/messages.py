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


import json
import re
from typing import Any, ClassVar, Dict, Tuple, Union, TYPE_CHECKING
from dataclasses import dataclass
from argparse import Namespace

from mkdocs.exceptions import BuildError


from .plugin.maestro_tools import dump_and_dumper

if TYPE_CHECKING:
    from .plugin.pyodide_macros_plugin import PyodideMacrosPlugin



Tr = Union['Msg', 'MsgPlural', 'Tip', 'TestsToken']
LangProp = str
Pattern = re.compile('')       # done this way for linting and mkdocstrings... :/





@dataclass
class JsDumper:
    """ Base class to automatically transfer "lang" messages from python to JS """
    # pylint: disable=no-member,missing-function-docstring

    PROPS: ClassVar[Tuple[str]] = tuple('msg plural em as_pattern kbd'.split())
    ENV: ClassVar[Dict[str,Any]] = None

    def __str__(self):
        return self.msg

    def dump_as_dct(self):
        dct = {
            prop: v for prop in self.PROPS if (v := self.get_prop(prop)) is not None
        }
        return dct


    def get_prop(self,prop):
        return str(self) if prop=='msg' else getattr(self, prop, None)


    @staticmethod
    def register_env(env:'PyodideMacrosPlugin'):
        JsDumper.ENV = {
            name: getattr(env,name) for name in "site_name".split()
        }
        JsDumper.ENV['tests'] = str(env.lang.tests) # pylint: disable=unsupported-assignment-operation



@dataclass
class Msg(JsDumper):
    """
    A simple message to display in the application.

    Parameters:
        msg: Message to use
    """
    msg: str



@dataclass
class MsgPlural(Msg):
    """
    A message that could be used in singular or plural version at runtime.

    Parameters:
        msg:        Message to use
        plural:     If not given, `msg+"s"` is used as plural.
    """
    plural: str = ''

    def __post_init__(self):
        self.plural = self.plural or self.msg+'s'

    def one_or_many(self, many:bool):
        return self.plural if many else self.msg





@dataclass
class TestsToken(JsDumper):
    """
    Specific delimiter used to separate the user's code from the public tests in an editor.
    Leading and trailing new lines used here will reflect on the editor content and will
    match the number of additional empty lines before or after the token itself.

    Because this token is also be converted to a regex used in various places, it has to
    follow some conventions.

    ___Ignoring leading and trailing new lines:___

    - The string must begin with `#`.
    - The string must not contain new line characters anymore.
    - Ignoring inner spaces, the token string must be at least 6 characters long.

    Parameters:
        msg:  Separator to use (with leading and trailing new lines).

    Raises:
        BuildError: If one of the above conditions is not fulfilled.
    """
    msg: str
    as_pattern = Pattern       # Overridden in post_init. Needed for types in 3.8

    def __post_init__(self):
        self.msg = f"\n{ self.msg }\n"
        s = self.msg.strip()
        short = s.replace(' ','').lower()

        if not s.startswith('#'):
            raise BuildError(
                "The public tests token must start with '#'"
            )
        if '\n' in s:
            raise BuildError(
                "The public tests token should use a single line"
                " (ignoring leading or trailing new lines)"
            )
        if short=='#test' or len(short)<6:
            raise BuildError(
                "The public tests token is too short/simple and could cause false positives."
                " Use at least something like '# Tests', or something longer."
            )

        pattern = re.sub(r'\s+', r"\\s*", s)
        self.as_pattern = re.compile(pattern, flags=re.I)

    def __str__(self):
        return self.msg.strip()

    def get_prop(self,prop):
        return (
            self.as_pattern.pattern if prop=='as_pattern' else
            self.msg if prop=='msg' else
            super().get_prop(prop)
        )




@dataclass
class Tip(JsDumper):
    """
    Data for tooltips.

    Parameters:
        em:     Width of the tooltip element, in em units (if 0, use automatic width).
        msg:    Tooltip message.
        kbd:    Keyboard shortcut (as "Ctrl+I", for example). Informational only (no
                impact on the behaviors)

    If a `kbd` combination is present, it will be automatically added in a new line
    after the tooltip `msg`.
    """
    em: int         # Width, in em. If 0, use automatic width
    msg: str        # tooltip message
    kbd: str = ""   # ex: "Ctrl+I" / WARNING: DO NOT MODIFY DEFAULTS!

    def __str__(self):
        msg = self.msg.format(**self.ENV)       # pylint: disable=not-a-mapping
        if self.kbd:
            kbd = re.sub(r"(\w+)", r"<kbd>\1</kbd>", self.kbd)
            msg = f"{ msg }<br>({ kbd })"
        return msg









class Lang(Namespace):
    # pylint: disable=no-member

    # LANG_TOKEN
    # Editors:
    tests:      Tr = TestsToken("\n# Tests\n")  ###
    """
    Séparateur placé entre le code utilisateur et les tests publics.

    * Les sauts de lignes situés au début ou à la fin indiquent le nombre de lignes vides avant
    ou après le texte lui-même.
    * Le séparateur lui-même doit commencer par `#` et avoir au moins 6 caractères (hors espaces).
    """###
    comments:   Tr = Tip(15, "(Dés-)Active le code après la ligne <code>{tests}</code> "
                             "(insensible à la casse)", "Ctrl+I")    ###
    """
    Info-bulle pour le bouton permettant d'activer ou désactiver les tests publics.
    La chaîne utilisée doit contenir `{tests}` car le contenu de TestsToken.msg y sera inséré.
    """###


    # Terminals
    feedback:      Tr = Tip(15, "Tronquer ou non le feedback dans les terminaux (sortie standard"
                                " & stacktrace / relancer le code pour appliquer)")    ###
    """
    Info-bulle du bouton contrôlant le "niveau de feedback" affiché dans le terminal
    """###
    wrap_term:     Tr = Tip(15, "Si activé, le texte copié dans le terminal est joint sur une "
                                "seule ligne avant d'être copié dans le presse-papier")    ###
    """
    Info-bulle du bouton indiquant si le texte copié depuis le terminal est join anat d'être copié ou non.
    """###
    run_script:    Tr = Msg("Script lancé...")    ###
    """
    Message annonçant le début des executions (pyodide).
    """###
    install_start: Tr = Msg("Installation de paquets python. Ceci peut prendre un certain temps...")    ###
    """
    Message affiché dans la console avant le chargement de micropip, en vue d'installer des modules manquants.
    """###
    install_done:  Tr = Msg("Installations terminées !")    ###
    """
    Message affiché lorsque les installation de paquets par micropip sont finies.
    """###
    success_msg:   Tr = Msg("Terminé sans erreur !")    ###
    """
    Message affiché à la fin des tests publics, si aucune erreur n'a été rencontrée.
    """###


    # Terminals: validation success/failure messages
    success_head:  Tr = Msg("Bravo !")    ###
    """
    Entête du message de succès (gras, italique, en vert)
    """###
    success_tail:  Tr = Msg("Pensez à lire")    ###
    """
    Fin du message de succès.
    """###
    fail_head:     Tr = Msg("Dommage !")    ###
    """
    Entête du message d'échec (gras, italique, en orange)
    """###
    reveal_corr:   Tr = Msg("le corrigé")    ###
    """
    Bout de phrase annonçant l'existence d'une correction.
    """###
    reveal_join:   Tr = Msg("et")    ###
    """
    Conjonction de coordination joignant reveal_corr et reveal_rem, quand correction et
    remarques sont présentes.
    """###
    reveal_rem:    Tr = Msg("les commentaires")    ###
    """
    Bout de phrase annonçant l'existence de remarques.
    """###
    success_head_extra:  Tr = Msg("Vous avez réussi tous les tests !")    ###
    """
    Fin du message annonçant un succès.
    """###
    fail_tail:     Tr = MsgPlural("est maintenant disponible", "sont maintenant disponibles") ###
    """
    Fin du message annonçant un échec.
    """###


    # Corr  rems admonition:
    title_corr: Tr = Msg('Solution')    ###
    """
    Utilisé pour construire le titre de l'admonition contenant la correction et les remarques,
    sous les IDEs.
    """###
    title_rem:  Tr = Msg('Remarques')   ###
    """
    Utilisé pour construire le titre de l'admonition contenant la correction et les remarques,
    sous les IDEs.
    """###
    corr:       Tr = Msg('🐍 Proposition de correction')    ###
    """
    Titre du bloc de code contenant la correction d'un IDE, dans l'admonition "correction &
    remarques".
    """###
    rem:        Tr = Msg('Remarques')    ###
    """
    Titre (équivalent &lt;h3&gt;) annonçant le début des remarques, dans l'admonition "correction &
    remarques"
    """###


    # Buttons, IDEs buttons & counter:
    py_btn:     Tr = Tip(9, "Exécuter le code")    ###
    """
    Info-bulle d'un bouton isolé, permettant de lancer un code python.
    """###
    play:       Tr = Tip(9,  "Exécuter le code", "Ctrl+S")    ###
    """
    Info-bulle du bouton pour lancer les tests publics.
    """###
    check:      Tr = Tip(9,  "Valider", "Ctrl+Enter")    ###
    """
    Info-bulle du bouton pour lancer les tests privés.
    """###
    download:   Tr = Tip(0,  "Télécharger")    ###
    """
    Info-bulle du bouton pour télécharger le contenu d'un éditeur.
    """###
    upload:     Tr = Tip(0,  "Téléverser")    ###
    """
    Info-bulle du bouton pour remplacer le contenu d'un éditeur avec un fichier stocké en local.
    """###
    restart:    Tr = Tip(0,  "Réinitialiser l'éditeur")    ###
    """
    Info-bulle du bouton réinitialisant le contenu d'un éditeur.
    """###
    save:       Tr = Tip(0,  "Sauvegarder dans le navigateur")    ###
    """
    Info-bulle du bouton pour enregistrer le contenu d'un éditeur dans le localStorage du
    navigateur.
    """###
    corr_btn:   Tr = Tip(0,  "Tester la correction (serve)")    ###
    """
    Info-bulle du bouton pour tester le code de la correction (uniquement durant `mkdocs serve`).
    """###
    show:       Tr = Tip(0,  "Afficher corr & REMs")    ###
    """
    Info-bulle du bouton pour révéler les solutions & REMs (uniquement durant `mkdocs serve`).
    """###
    attempts_left: Tr = Msg("Évaluations restantes")    ###
    """
    Info-bulle du bouton pour enregistrer le contenu d'un éditeur dans le localStorage du
    navigateur.
    """###


    # QCMS
    qcm_title:     Tr = MsgPlural("Question")    ###
    """
    Titre utilisé par défaut pour les admonitions contenant les qcms (si pas d'argument renseigné
    dans l'appel de la macro `multi_qcm`).
    """###
    qcm_mask_tip:  Tr = Tip(15, "Les réponses resteront cachées...")    ###
    """
    Info-bulle affichée au survol du masque, pour les qcms dont les réponses ne sont pas révélées.
    """###
    qcm_check_tip: Tr = Tip(11, "Vérifier les réponses")    ###
    """
    Info-bulle du bouton de validation des réponses des qcms.
    """###
    qcm_redo_tip:  Tr = Tip(9,  "Recommencer")    ###
    """
    Info-bulle du bouton de réinitialisation des qcms.
    """###


    # Others
    tip_trash: Tr = Tip(15, "Supprimer du navigateur les codes enregistrés pour {site_name}") ###
    """
    Info-bulle du bouton de pour supprimer les données stockées dans le navigateur
    (la poubelle en haut à côté de la barre de recherche).
    Le nom du site (`site_name` dans `mkdocs.yml`) est automatiquement intégré dans la phrase
    avec "{site_name}".
    """###

    figure_text: Tr = Msg("Votre tracé sera ici") ###
    """
    Texte affiché avent qu'une `figure` ne soit dessinée (voir à propos des dessins faits avec
    `matplotlib` et la macro `figure(...)`).
    """###
    figure_admo_title: Tr = Msg("Votre figure") ###
    """
    Titre données aux admonitions contenant des "figures" (voir à propos des dessins faits avec
    `matplotlib` et la macro `figure(...)`).
    """###

    picker_failure: Tr = Msg(
        "Veuillez cliquer sur la page entre deux utilisations des raccourcis clavier ou utiliser "
        "un bouton, afin de pouvoir téléverser un fichier."
    ) ###
    """
    Message s'affichant dans le navigateur si l'utilisateur essaie de lancer un code utilisant
    `pyodide_uploader_async` via un raccourci après avec annuler le chargement une première fois :
    ceci n'est pas considéré comme une "action utilisateur" par certains navigateurs.

    Nota: les utilisateur de navigateurs non compatibles avec HTMLInputElement.showPicker n'auront
    jamais cette information.
    """###


    # LANG_TOKEN
    #-------------------------------------------------------------------------



    def overload(self, dct: Dict[LangProp,Tr]):
        """
        Overloads the defaults with any available user config data.
        This has to be done at macro registration time (= in a `define_env(env)` function).

        @throws BuildError if:
        *
        """
        for k,v in dct.items():
            current = getattr(self,k, None)

            if current is None:
                raise BuildError(f"Invalid Lang property: {k!r}")
            if not isinstance(v, current.__class__):
                kls = current.__class__.__name__
                raise BuildError(f"Invalid Translation type: {v!r} should be an instance of {kls}")
            setattr(self,k,v)


    def register_env(self, env:'PyodideMacrosPlugin'):
        """ Register the config data in the JsDumper class (for messages rendering) """
        JsDumper.register_env(env)


    @classmethod
    def dump_as_str(cls, obj=None):
        """
        Create a complete json object with all teh string representations of all the messages.
        - Takes potential overloads in consideration
        - WARNING: js dumps are simple str conversions, so far, so some messages might be
                   missing some information... (specifically, plurals)
        - If obj is None, use null for all values.
        """
        dct = dump_and_dumper(cls.__annotations__, obj, lambda v: v.dump_as_dct() if v else "null")
        if obj:
            return json.dumps(dct)

        return json.dumps(dct, indent=8).replace('"','')
