
from pyodide_mkdocs_theme.pyodide_macros import (
    PyodideMacrosPlugin,
    Msg, MsgPlural, TestsToken, Tip,
)


def define_env(env:PyodideMacrosPlugin):
    """ The customization has to be done at macro definition time.
        You could paste the code inside this function into your own main.py (or the
        equivalent package if you use a package instead of a single file). If you don't
        use personal macros so far, copy the full code into a `main.py` file at the root
        of your project (note: NOT in the docs_dir!).

        NOTE: you can also completely remove this file if you don't want to use personal
              macros or customize the messages in the built documentation.

        * Change whatever string you want.
        * Remove the entries you don't want to modify
        * Do not change the keyboard shortcuts for the Tip objects: the values are for
          informational purpose only.
        * See the documentation for more details about which string is used for what
          purpose, and any constraints on the arguments:
          https://frederic-zinelli.gitlab.io/pyodide-mkdocs-theme/custom/messages/

        ---

        The signatures for the various objects below are the following:

        ```python
        Msg(msg:str)
        MsgPlural(msg:str, plural:str="")
        Tip(width_in_em:int, msg:str, kbd:str=None)
        TestsToken(token_str:str)
        ```
    """

    custom = {
    # Editors:
        "tests":      TestsToken("\n# Tests\n"),
        "comments":   Tip(15, "(Dés-)Active le code après la ligne <code>{tests}</code> "
                             "(insensible à la casse)", "Ctrl+I"),


    # Terminals
        "feedback":      Tip(15, "Tronquer ou non le feedback dans les terminaux (sortie standard"
                                " & stacktrace / relancer le code pour appliquer)"),
        "wrap_term":     Tip(15, "Si activé, le texte copié dans le terminal est joint sur une "
                                "seule ligne avant d'être copié dans le presse-papier"),
        "run_script":    Msg("Script lancé..."),
        "install_start": Msg("Installation de paquets python. Ceci peut prendre un certain temps..."),
        "install_done":  Msg("Installations terminées !"),
        "success_msg":   Msg("Terminé sans erreur !"),


    # Terminals: validation success/failure messages
        "success_head":  Msg("Bravo !"),
        "success_tail":  Msg("Pensez à lire"),
        "fail_head":     Msg("Dommage !"),
        "reveal_corr":   Msg("le corrigé"),
        "reveal_join":   Msg("et"),
        "reveal_rem":    Msg("les commentaires"),
        "success_head_extra":  Msg("Vous avez réussi tous les tests !"),
        "fail_tail":     MsgPlural("est maintenant disponible", "sont maintenant disponibles"),


    # Corr  rems admonition:
        "title_corr": Msg('Solution'),
        "title_rem":  Msg('Remarques'),
        "corr":       Msg('🐍 Proposition de correction'),
        "rem":        Msg('Remarques'),


    # Buttons, IDEs buttons & counter:
        "py_btn":     Tip(9, "Exécuter le code"),
        "play":       Tip(9,  "Exécuter le code", "Ctrl+S"),
        "check":      Tip(9,  "Valider", "Ctrl+Enter"),
        "download":   Tip(0,  "Télécharger"),
        "upload":     Tip(0,  "Téléverser"),
        "restart":    Tip(0,  "Réinitialiser l'éditeur"),
        "save":       Tip(0,  "Sauvegarder dans le navigateur"),
        "corr_btn":   Tip(0,  "Tester la correction (serve)"),
        "show":       Tip(0,  "Afficher corr & REMs"),
        "attempts_left": Msg("Évaluations restantes"),


    # QCMS
        "qcm_title":     MsgPlural("Question"),
        "qcm_mask_tip":  Tip(15, "Les réponses resteront cachées..."),
        "qcm_check_tip": Tip(11, "Vérifier les réponses"),
        "qcm_redo_tip":  Tip(9,  "Recommencer"),


    # Others
        "tip_trash": Tip(15, "Supprimer du navigateur les codes enregistrés pour {site_name}"),

        "figure_text": Msg("Votre tracé sera ici"),
        "figure_admo_title": Msg("Votre figure"),

        "picker_failure": Msg(
        "Veuillez cliquer sur la page entre deux utilisations des raccourcis clavier ou utiliser "
        "un bouton, afin de pouvoir téléverser un fichier."
    )
    }

    env.lang.overload(custom)
