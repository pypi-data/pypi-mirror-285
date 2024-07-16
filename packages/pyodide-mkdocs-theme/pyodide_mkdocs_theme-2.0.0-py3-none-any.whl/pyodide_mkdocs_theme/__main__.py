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

import sys
from pathlib import Path
from argparse import ArgumentParser
from contextlib import redirect_stdout


from .__version__ import __version__

PMT_SCRIPTS = 'scripts'



parser = ArgumentParser(
    'pyodide_mkdocs_theme',
    description = "Scripts for pyodide-mkdocs-theme",
    epilog = "Copyleft GNU GPLv3 🄯 2024 Frédéric Zinelli. "
             "This program comes with ABSOLUTELY NO WARRANTY."
)
parser.add_argument(
    '-V', '--version', action='version', version=f'pyodide-mkdocs-theme {__version__}'
)
parser.add_argument(
    '-n', '--new', default="",
    help='Starts a new PMT project, creating a directory with the given name in the current '
         'folder, then adds some basic contents to the directory (docs and examples, mkdocs.yml, '
         'requirements.txt, main.py, pyodide_plot.py).'
)
parser.add_argument(
    '--mime', action='store_true',
    help='Open a page in the browser, to the MDN documentation about MIME types (useful '
         'when using pyodide_downloader).'
)
parser.add_argument(
    '--lang', action='store_true',
    help='Print the base python code to customize some messages.'
)
parser.add_argument(
    '--plot', action='store_true',
    help='Print the content of the PyodidePlot declaration file, helping to run it locally.'
)
parser.add_argument(
    '--py', action='store_true',
    help='Print an example of python file, for {{IDE(...)}} or {{terminal(...)}} macros'
)
parser.add_argument(
    '--yml', action='store_true',
    help='Print a base configuration for the mkdocs.yml file.'
)
parser.add_argument(
    '-F', '--file', default="",
    help='When used in combination with one of --lang, --py or --yml, the information will '
         'be written into the given file instead of the stdout (any existing content will '
         'be overwritten / use an absolute path or a path relative to the cwd).'
)



def main():
    # pylint: disable=multiple-statements


    def get_script(pathname:str):
        path = Path(__file__).parent / PMT_SCRIPTS
        for segment in pathname.split('/'):
            path /=  segment
        return path



    def display(filename:str):
        """ Display the base code for GUI messages customizations """

        src = get_script(filename)
        txt = src.read_text(encoding='utf-8')
        print(txt)

    def inner():
        if args.lang:   display('main.py')
        elif args.plot: display('pyodide_plot.py')
        elif args.py:   display('docs/exo.py')
        elif args.yml:  display('mkdocs.yml')



    def initiate_project(folder):
        project = Path(folder)
        project.mkdir(parents=True)     # raise if already exists

        src = get_script('mkdocs.yml').parent
        for file in src.rglob('*.*'):
            if file=='__init__.py':
                continue
            target = project / file.relative_to(src)

            target.parent.mkdir(exist_ok=True)
            content = file.read_bytes()
            target.touch()
            target.write_bytes(content)



    #------------------------------------------------------------------------


    if len(sys.argv) < 2:
        sys.argv.append('-h')

    args = parser.parse_args()

    if args.mime:
        page = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types"
        import webbrowser
        webbrowser.open(page, new=2)

    elif args.new:
        initiate_project(args.new)

    elif not args.file:
        inner()
    else:
        path = Path(args.file)
        path.touch(exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f, redirect_stdout(f):
            inner()



if __name__ == '__main__':
    main()
