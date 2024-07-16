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
from pathlib import Path
from dataclasses import dataclass
import subprocess
from typing import ClassVar, Dict, Optional, Union

from mkdocs.exceptions import BuildError

from ..plugin.maestro_IDE import MaestroIDE
from ..paths_utils import read_file
from ..pyodide_logger import logger
from ..tools_and_constants import ScriptSection, SiblingFile




CWD = Path.cwd()




@dataclass
class IdeFilesExtractor:
    """
    ENTRY POINT: takes a py_name (IDE macro first argument) and extract from that all the
    necessary data from the different files.

    With `py_name` being denoted {X} and {F} being the stem of the current .md source file,
    the extracted files may be:

        1.  {X}.py
            {X}_REM.md
            {X}_VIS_REM.md
            Where the py file contains all the needed python code/sections, separated by the
            pyodide python tokens: `# --- PYODIDE:{kind} --- #`

        2.  {X}.py
            {X}_text.py
            {X}_corr.py
            {X}_REM.md
            {X}_VIS_REM.md

        3.  scripts/{F}/{X}.py
            scripts/{F}/{X}_REM.md
            scripts/{F}/{X}_VIS_REM.md
            Where the py file contains all the needed python code/sections, separated by the
            pyodide python tokens: `# --- PYODIDE:{kind} --- #`

        4.  scripts/{F}/{X}.py
            scripts/{F}/{X}_test.py
            scripts/{F}/{X}_corr.py
            scripts/{F}/{X}_REM.md
            scripts/{F}/{X}_VIS_REM.md

    The order gives the precedence. Way "1" is excluding the 2 others (except for the REM file)
    """

    env: MaestroIDE
    py_name: str
    # id: Optional[int] = None

    #-----------------------------

    exo_py: Optional[Path] = None
    """ Path to the master python file (if any) """

    file_max_attempts: Union[int, str] = ""
    """ [deprecated] """

    test_rel_path: Optional[Path] = None
    """ Relative path to the ..._test.py file (or None if no file) """

    corr_rel_path: Optional[Path] = None
    """ Relative path to the ..._corr.py file (or None if no file) """

    rem_rel_path: Optional[Path] = None
    """ Relative path to the ...REM.md file (or None if no file) """

    vis_rem_rel_path: Optional[Path] = None
    """ Relative path to the ..._VIS_REM.md file (or None if no file) """


    corr_rems_bit_mask: int = 0
    """ Bit mask giving the configuration for correction and/or remark data
        mask&1 represent the presence of correction, mask&2 is for REM.
    """

    env_content: str = ""
    """ Python header code content (run async) """

    env_term_content: str = ""
    """ Run unconditionally, only before a command of a terminal is run. """

    user_content:str = ""
    """ Python user code (only) """

    corr_content: str = ""
    """ Python solution code """

    public_tests: str = ""
    """ Public tests (only) """

    secret_tests:str = ""
    """ Code for the private tests """

    post_term_content: str = ""
    """ Run unconditionally, only after a command of a terminal was run. """

    post_content: str = ""
    """ Code for post executions (teardown / run async).
        Always run, even in case of failures in users or tests code, but NOT if an error
        occurred in the ENV section.
    """



    #------------------------------------------------------------

    # skip_check: bool = False
    # """
    # If True, the sanity check about the presence of secret tests vs corr&REM, and the
    # python code checks will be skipped.
    # """


    SECTION_TOKEN: ClassVar[re.Pattern] = re.compile(
        r'^(# *-+ *PYODIDE *: *\w+ *-+ *#)$', flags=re.MULTILINE
    )

    SECTION_TO_PROP: ClassVar[Dict[str,str]] = {
        ScriptSection.env:          "env_content",
        ScriptSection.env_term:     "env_term_content",
        ScriptSection.user:         "user_content",
        ScriptSection.corr:         "corr_content",
        ScriptSection.tests:        "public_tests",
        ScriptSection.secrets:      "secret_tests",
        ScriptSection.post_term:    "post_term_content",
        ScriptSection.post:         "post_content",
    }


    @property
    def has_env(self):
        return bool(self.env_content)
    @property
    def has_code(self):
        return bool(self.user_content)
    @property
    def has_corr(self):
        return bool(self.corr_content)
    @property
    def has_tests(self):
        return bool(self.public_tests)
    @property
    def has_secrets(self):
        return bool(self.secret_tests)
    @property
    def has_post(self):
        return bool(self.post_content)
    @property
    def has_rem(self):
        return bool(self.rem_rel_path)
    @property
    def has_vis_rem(self):
        return bool(self.vis_rem_rel_path)


    #------------------------------------------------------------


    def __post_init__(self):

        self.exo_py: Optional[Path] = self.env.get_sibling_of_current_page(self.py_name, tail='.py')
        if not self.exo_py and self.py_name:
            raise BuildError(
                f"No python file could be found for py_name='{ self.py_name }', "
                f"in { self.env.file_location() }"
            )

        script_content = read_file(self.exo_py) if self.exo_py  else ""

        # Extract everything:
        if self.SECTION_TOKEN.search(script_content):
            self.extract_multi_sections(script_content)
        else:
            self.extract_multi_files(script_content)

        self.corr_rems_bit_mask = self.has_corr + (self.has_rem or self.has_vis_rem) * 2

        # if not self.skip_check and self.env.check_python_files:
        #     self.check_python()

        # self._fuuuuuusion()
        # self._cleanup_tests()


    def get_sections_data(self, with_corr=True):
        """ Returns an generator of tuples (property, content) for all sections. """
        return (
            (prop, getattr(self, prop))
            for prop in self.SECTION_TO_PROP.values()
            if prop != "corr_content" or  with_corr
        )



    def get_path_and_existence(self, tail:str):
        """
        Return a pair (Path|None, str).
        The path|None is the built path, relative to the CWD, or None if no file is found.
        The string is the file content (empty string if no file)

        @throws: BuildError if a file is found but it's empty.
        """
        content = ''
        path: Union[Path,None] = self.env.get_sibling_of_current_page(self.py_name, tail=tail)

        if path:
            path = path.relative_to(CWD)

            # Also checks that the file exists and contains something:
            if not path.is_file():
                path = None
            else:
                content = read_file(path).strip()
                if not content:
                    raise BuildError(f"{path} is an empty file and should be removed.")
        return path, content




    #--------------------------------------------------------------------------
    #                      MONOLITHIC WAY (= theme way)
    #--------------------------------------------------------------------------


    def extract_multi_sections(self, script_content:str):
        """
        Extract all the python content from one unique file with different sections:
            - HDR: header content (optional)
            - user: starting code for the user (optional)
            - corr: ... (optional - must be defined before the tests...?)
            - tests: public tests (optional)
            - secrets: secrets tests (optional)
        Note that the REM content has to stay in a markdown file, so that it can contain macros
        and mkdocs will still interpret those (if it were containing only markdown, it could be
        inserted on the fly by a macro, but an "inner macro call" would be ignored).
        """

        chunks = self.SECTION_TOKEN.split(script_content)
        chunks = [*filter(bool, map(str.strip, chunks))]
        pairs  = [*zip(*[iter(chunks)]*2)]


        # File structure validations:
        headers = [ self._extract_section_name(section)
                        for section in chunks if self.SECTION_TOKEN.match(section) ]
        odds_sections = len(chunks) & 1
        wrong_tic_toc = len(headers) != sum(
            bool(self.SECTION_TOKEN.match(header)) for header,_ in pairs
        )
        if odds_sections or wrong_tic_toc:
            raise BuildError(
                f"Invalid file structure for { self.exo_py }: no empty sections allowed."
            )
        no_ignores_headers = [ h for h in headers if h != ScriptSection.ignore ]
        if len(no_ignores_headers) != len(set(no_ignores_headers)):
            raise BuildError(
                f"Invalid file structure for { self.exo_py }: Duplicate sections are not "
                "allowed (except for the `ignore` section)."
            )

        # Codes registrations:
        for section,content in pairs:
            section_name = self._extract_section_name(section)
            if section_name == ScriptSection.ignore:
                continue
            prop = self._get_section_property(section_name)
            setattr(self, prop, content)

        self.rem_rel_path, _     = self.get_path_and_existence(SiblingFile.rem)
        self.vis_rem_rel_path, _ = self.get_path_and_existence(SiblingFile.vis_rem)



    @staticmethod # because, pylint...
    def _extract_section_name(header:str):
        return header.strip(' #-').split(':')[-1].strip()


    def get_section(self, section:ScriptSection):
        """ Extract the given section """
        prop = self._get_section_property(section)
        return  getattr(self, prop)


    def _get_section_property(self, section:ScriptSection):
        if section not in self.SECTION_TO_PROP:
            raise BuildError(f'Unknown section name {section!r} in { self.exo_py }')
        else:
            return self.SECTION_TO_PROP[section]




    #--------------------------------------------------------------------------
    #                            OLD FASHION WAY
    #--------------------------------------------------------------------------


    def extract_multi_files(self, script_content:str):
        """
        "Old fashion way" extractions, with:
            - user code + public tests (+ possibly HDR) in the base script file (optional)
            - secret tests in "{script}_test.py" (optional)
            - Correction in "{script}_corr.py" (optional, but secret tests have to exist)
            - Remarks in "{script}_REM.md" (optional, but secret tests have to exist)
        """
        if script_content.startswith('#MAX'):
            logger.error(
                "Setting IDE MAX value through the file is deprecated. Move this to the IDE macro "
                f"argument.\nFile: { self.exo_py }"
            )
            script = script_content
            first_line, script = script.split("\n", 1) if "\n" in script else (script,'')

            script_content = script.strip()
            self.file_max_attempts = first_line.split("=")[1].strip()

        (
            self.env_content, self.user_content, self.public_tests,
        ) = self.env.get_hdr_and_public_contents_from(script_content)

        (
            (self.test_rel_path, self.secret_tests),
            (self.corr_rel_path, self.corr_content),
            (self.rem_rel_path,  _),
            (self.vis_rem_rel_path,  _),
        ) = map(self.get_path_and_existence, (
            SiblingFile.test, SiblingFile.corr, SiblingFile.rem, SiblingFile.vis_rem,
        ))

        self.secret_tests = "" if not self.secret_tests else read_file(self.test_rel_path)




    #--------------------------------------------------------------------------
    #                            PYTHON CHECKS
    #--------------------------------------------------------------------------


    def check_python(self):
        """
        * hdr + corr + public + secret => pass
        * hdr + user + public => doesn't pass
        * hdr + user + secret => doesn't pass
        """
        raise ValueError("The plugin option `build.check_python_files` has been disabled.")
        if not self.py_name: # or self.id is not None:
            # skip: nothing to check
            return

        src    = self.env.get_sibling_of_current_page(self.py_name, tail='.py')
        target = Path('___XXX_check_python.py')
        target.touch(exist_ok=True)

        to_check = [
            (
                "Correction code should have passed", True, bool(self.corr_content and self.secret_tests),
                [self.env_content, self.corr_content, self.public_tests, self.secret_tests],
            ),
            (
                "Initial solution should fail public tests", False, True,
                [self.env_content, self.user_content, self.public_tests],
            ),
            (
                "Initial solution should fail public + secret tests", False, bool(self.secret_tests),
                [self.env_content, self.user_content, self.public_tests, self.secret_tests],
            ),
        ]
        try:
            for msg, does_run, todo, sections in to_check:

                if not todo: continue

                content = '\n\n'.join(sections)
                target.write_text(content, encoding='utf-8')
                msg += f" for { src.relative_to(CWD) }"
                kwargs = dict(shell=True, check=True, capture_output=True, timeout=2)

                if does_run:
                    try:
                        subprocess.run(f'python {target}', **kwargs)
                    except Exception as e:
                        print(e)
                        if self.env.soft_check:
                            logger.error(msg)
                        else:
                            raise BuildError(msg) from e
                else:
                    try:
                        subprocess.run(f'python {target}', **kwargs)
                        if self.env.soft_check:
                            logger.error(msg)
                        else:
                            raise BuildError(msg)
                    except: pass                    # pylint: disable=all

        finally:
            # final file cleanup
            target.unlink()






    #--------------------------------------------------------------------------
    #        PYTHON FILES MANAGEMENT IN BATCHES (used on CodEx only)
    #--------------------------------------------------------------------------



    # def _fuuuuuusion(self):
    #     src = self.env.get_sibling_of_current_page(self.py_name, tail=SiblingFile.exo)
    #     if not src:
    #         return
    #     alter = 'fusion_tmp' / src.relative_to(self.env.docs_dir_path)
    #     # print(alter)
    #     self.__create_merged_file(alter)


    # def _cleanup_tests(self):
    #     target_prop = 'corr_content'
    #     content_to_cleanup:str = getattr(self, target_prop)
    #     if self.public_tests and self.public_tests in content_to_cleanup:
    #         cuts = [*map(str.strip, content_to_cleanup.split(self.public_tests))]
    #         print(f"TESTS - {self.exo_py} : n_parts={ len(cuts) }") # | { cuts[0].strip() }")
    #         assert len(cuts)==2

    #         start,end = cuts
    #         start = re.sub(r'(?i)# *tests?$', '', start, flags=re.MULTILINE).strip()
    #         setattr(self, target_prop, start+"\n"+end)

    #         src = self.env.get_sibling_of_current_page(self.py_name, tail=SiblingFile.exo)
    #         alter = 'fusion_tmp' / src.relative_to(self.env.docs_dir_path)
    #         self.__create_merged_file(alter)



    # def __create_merged_file(self, merge_file:Path):
    #     order = [
    #         (section, getattr(self, self.SECTION_TO_PROP[section]))
    #              for section in [
    #                                 ScriptSection.env,
    #                                 ScriptSection.user,
    #                                 ScriptSection.corr,
    #                                 ScriptSection.tests,
    #                                 ScriptSection.secrets,
    #                             ]]
    #     merged = ''.join(
    #         f"\n\n\n# --------- PYODIDE:{ section } --------- #\n\n{ content }"
    #             for section,content in order
    #             if content
    #     )

    #     merge_file.parent.mkdir(parents=True, exist_ok=True)
    #     merge_file.touch(exist_ok=True)
    #     merge_file.write_text(merged, encoding='utf-8')
