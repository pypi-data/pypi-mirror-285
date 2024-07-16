/*
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
*/



/**Special JS Error: methods calls exclusions are tested from the JS runtime, instead of pyodide.
 * So, JS has to throw a special error that will mimic ("enough"...) the pattern of pyodide errors
 * and hance, will be considered legit errors.
 */
class PythonError extends Error {
    toString(){ return "Python" + super.toString() }
}






/**Function injected into the python environment (must be defined earlier than others
 * to be used in the tweaked import function)
 * */
function inputWithPrompt(text) {
    let result = prompt(text);
    $.terminal.active().echo(result);
    return result;
}


function config(){ return CONFIG }


const pyodideFeatureCode=(()=>{

    const PYODIDE_SNIPPETS = {

    autoRun: `
def _hack_auto_run():
    G = globals()
    class AutoRunner:
        run = set()
        def __init__(self):
            self.strict = ${ CONFIG._devMode ? "True":"False" }
        def __call__(self, func):
            func()
            self.run.add(func.__name__)     # Skip registration if failure in func
        def clean(self):
            for k in self.run:
                if self.strict or k in G: del G[k]
            self.run.clear()
        def __repr__(self):
            return "AutoRunner()"

    __builtins__.auto_run = AutoRunner()
_hack_auto_run()
del _hack_auto_run
`,


    inputPrompt: `
@__builtins__.auto_run
def _hack_input_prompt():
    if not getattr(__builtins__, '__js_input__',None):
        import js
        __builtins__.__js_input__ = js.inputWithPrompt
    __builtins__.input = __js_input__
`,


    version: `
def version():
    print("pyodide-mkdocs-theme v${ CONFIG.version }")
`,


    exclusionsTools: `
@__builtins__.auto_run
def _hack_exclusions_tools():

    type = __builtins__.type      # avoid restrictions troubles

    def __move_forward__(stuff):
        treasure = __builtins__.__builtins___
        if type(stuff) is str and stuff in treasure:
            return treasure[stuff][0]

    class ExclusionError(Exception):
        @staticmethod
        def throw(that:str):
            raise ExclusionError(f"${ CONFIG.MSG.exclusionMarker }: don't use {that}")

    __builtins__.__move_forward__ = __move_forward__
    __builtins__.ExclusionError = ExclusionError
`,


    refresher: `
@__builtins__.auto_run
def _hack_scope_cleaner():

    # Avoid restrictions troubles:
    set = __builtins__.set
    globals = __builtins__.globals

    def clear_scope(skip=()):
        keeper = set(skip) | {
            '__name__', '__doc__', '__package__', '__loader__', '__spec__',
            '__annotations__', '__builtins__', '_pyodide_core', 'version'
        }
        g_dct = globals()
        for k in set(g_dct) - keeper:
            del g_dct[k]

    __builtins__.clear_scope = clear_scope
`,

    wantedImports: `
@__builtins__.auto_run
def _hack_find_imports():
    from pyodide.code import find_imports
    __builtins__.imported_modules = find_imports({FORMAT_TOKEN})

__builtins__.imported_modules
`,


    alreadyImported: `
@__builtins__.auto_run
def _hack_imported():
    import sys
    __builtins__.loaded_modules = " ".join(sys.modules.keys())

__builtins__.loaded_modules
`,


    upDownLoader: `
@__builtins__.auto_run
def _hack_uploader_downloader():

    import js
    from pyodide.ffi import create_proxy
    from typing import Callable, Any, Literal
    from argparse import Namespace

    class ReadAs(Namespace):
        txt = 'readAsText'
        bytes = 'readAsArrayBuffer'
        img = 'readAsDataURL'

        @classmethod
        def get_props(cls):
            return ', '.join(
                repr(p) for p in dir[cls] if not p.startswith('_') and p != 'get_props'
            )


    def wrapping(
        cbk: Callable[[str],Any],
        *,
        read_as: Literal["txt","bytes","img"] = 'txt',
        with_name:bool = False,
        multi:bool = False,
    ):
        read_method = getattr(ReadAs, read_as, None)
        if not read_method:
            raise ValueError(
                f"Invalid read_as argument: {read_as!r}. Available options are: {ReadAs.get_props()}"
            )

        def wrapper(content:str, filename:str, is_last:bool):

            if read_method == ReadAs.bytes:
                content = bytes(js.Uint8Array.new(content))

            args = (content, filename) if with_name else (content,)
            out.append(cbk(*args))

            if is_last:
                proxy_cbk.destroy()

        proxy_cbk = create_proxy(wrapper)    # Does NOT work when using pyodide.ffi.create_once_callable
        out = []

        return (proxy_cbk, read_method, multi), lambda: out


    async def pyodide_uploader_async(*args, **kw) -> Any :
        js_args, out_getter = wrapping(*args, **kw)
        await js.uploaderAsync(*js_args)
        out = out_getter()
        if kw.get('multi'):
            return tuple(out)
        return out.pop() if out else None

    def pyodide_uploader(*args, **kw) -> None :
        js_args, _ = wrapping(*args, **kw)
        js.uploader(*js_args)


    def pyodide_downloader(content:str|bytes|list[int], filename:str, type="text/plain"):
        if not isinstance(content, str):
            content = js.Uint8Array.new(content)
        js.downloader(content, filename, type)


    __builtins__.pyodide_uploader_async = pyodide_uploader_async
    __builtins__.pyodide_uploader       = pyodide_uploader
    __builtins__.pyodide_downloader     = pyodide_downloader
`,


    pyodidePlot: `
@__builtins__.auto_run
def _hack_plot():
    # THIS IS A PLOT TOKEN

    import matplotlib
    import matplotlib.pyplot as plt
    from typing import Callable, Sequence


    import js
    matplotlib.use("module://matplotlib_pyodide.html5_canvas_backend")


    class PyodidePlot:
        """
        Helper class, to draw figures from pyodide runtime, into a specified html element.
        If no argument is provided, the default \`div_id\` is used (arguments configuration of
        the plugin).

        Use as a remplacement for \`matplotlib.pyplot\`:

        \`\`\`python
        pyo_plt = PyodidePlot()
        pyo_plt.plot(xs, ys, ...)           # Same as pyplot.plot, but draw where appropriate
        pyo_plt.title("...")
        pyo_plt.show()
        \`\`\`

        Or draw quickly single curves:

        \`\`\`python
        pyo_plt = PyodidePlot("figure_id")
        pyo_plt.plot_func(                  # draw where appropriate + automatic plt.show()
            lambda x: x**3,
            range(-15, 16),
            'r-",
            "cube...",
        )
        \`\`\`
        """

        def __init__(self, div_id:str=''):
            self.div_id = div_id or js.config().argsFigureDivId

        def __getattr__(self, prop:str):
            return getattr(plt, prop)

        def _refresh(self):
            js.document.pyodideMplTarget = js.document.getElementById(self.div_id)
            js.document.getElementById(self.div_id).textContent = ""
            _,ax = plt.subplots()
            return ax


        def plot_func(
            self,
            func:Callable,
            rng:Sequence,
            fmt:str=None,
            title:str=None,
            *,
            show:bool=True
        ):
            """
            Draw an automatic graph for the given function on the given range, then "show"
            automatically the resulting graph in the correct figure element in the page.

            Arguments:
                func:  Callable, func(x) -> y
                rng:   Sequence of xs
                fmt:   Curve formatting (just like \`pyplot.plot\`)
                title: If given, will be added as title of the graph.
                show:  Call \`pyplot.show()\` only if \`True\`. This allows to customize the graph
                       before applying show manually.
            """

            xs = list(rng)
            ys = [*map(func, rng)]
            args = (xs,ys) if fmt is None else (xs,ys,fmt)
            ax = self._refresh()
            ax.plot(*args)
            if title: plt.title(title)
            if show:
                plt.show()


        def plot(self, *args, **kw):
            """
            Generic interface, strictly equivalent to \`pyplot.plot\`, except the \`PyodidePlot\`
            instance will automatically apply the drawing to the desired html element it is
            related to.

            _Use specifically this method to "plot"_ ! You then can rely on \`pyplot\` to finalize
            the figure as you prefer.
            """
            ax = self._refresh()
            return ax.plot(*args, **kw)

# THIS IS A PLOT TOKEN
    __builtins__.PyodidePlot = PyodidePlot
`,


    mermaidDrawer: `
@__builtins__.auto_run
def _hack_mermaid():
    import js

    def mermaid_figure(div_id:str=None):
        """
        Create a Callable[[str],None] that will draw the given mermaid code into the wanted figure div.
        """
        div_id = div_id or js.config().argsFigureDivId

        def to_mermaid(code:str, debug=False):
            if debug: print(code)
            code = f'<pre class="mermaid">{ code }</pre>'
            js.document.getElementById(div_id).innerHTML = code

        return to_mermaid

    try:
        if js.config().needMermaid:
            js.mermaid
        else:
            def mermaid_figure(*_,**__):
                raise ValueError(
                     "The function mermaid_figure cannot be used because there is no registration"
                    +" in the page.\\n\\nDon't forget to mark the markdown page by using the "
                    +"argument 'MERMAID=True' in one of the macros (IDE, IDEv, terminal or py_btn)"
                )
    except:
        raise ValueError(
            "Cannot create mermaid logistic: the js mermaid object doesn't exist."
            +"\\n\\nDon't forget to mark the markdown page by using the argument "
            +"'MERMAID=True' in one of the macros (IDE, IDEv, terminal or py_btn)"
        )

    __builtins__.mermaid_figure = mermaid_figure
`,

    // Cannot be done using the decorator, because called _before_ pyodide features refresh.
    setupStdIO: `
def _hack_stdout_up():
    import sys, io
    __builtins__.src_stdout = sys.stdout
    sys.stdout = io.StringIO()
_hack_stdout_up()
del _hack_stdout_up
`,


    getFullStdIO:`
@__builtins__.auto_run
def _hack_stdout_down():
    import sys
    __builtins__._stdout = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = __builtins__.src_stdout
    del __builtins__.src_stdout

__builtins__._stdout
`,
    }

    return (option, repl=null)=>{
        jsLogger('[checkPoint] - Pyodide feature:', option)
        let code = PYODIDE_SNIPPETS[option]
        if(code===undefined) throw new Error(`Unknown snippet: ${option}`)
        if(repl!==null){
            code = code.replace(/\{FORMAT_TOKEN\}/g, JSON.stringify(repl))
        }
        return code+"\n"
    }
})()


/**Delete all the variables in the global scope that left hanging by the AutoRunner instance.
 * */
const pyodideCleaner=()=>pyodide.runPython('__builtins__.auto_run.clean()')




/*
------------------------------------------------------------------
          Manage python stdout redirection in terminal
------------------------------------------------------------------
*/


/**Use a StringIO stdout, so that the full content can be extracted later
 * */
const setupStdIO =_=>{
    const code = pyodideFeatureCode('setupStdIO')
    return pyodide.runPython(code)
}

const getFullStdIO =_=>{
    const code = pyodideFeatureCode('getFullStdIO')
    return escapeSquareBrackets( pyodide.runPython(code) || '' )
}







/*
------------------------------------------------------------------
                      Manage code exclusions
------------------------------------------------------------------
*/


/**Put in place code exclusions. Are handled:
 *   - builtin function calls
 *   - imports
 *   - method calls (done through a simple string check in the code, in runPythonCodeWithOptionsIfNoStdErr)
 *
 *
 * ## RATIONALS:
 *
 * To forbid the use of some functions or packages, replace them in the global scope by "functions"
 * that look "more or less the same", but will raise an error when called, or when used in the
 * wrong way (imports).
 *
 *
 * ## PROBLEMS:
 *
 * 1. Pyodide itself uses various functions to run python code:
 *      - eval is used in pyodide.runPython
 *      - reversed and/or min and/or max may be used when building a stacktrace when an error is
 *        thrown in python
 * 2. This forbids to replace the __builtins__ versions of those functions (see about imports)
 * 3. but the __main__ script is run separately of pyodide actual "python runtime".
 *
 *
 * ## SOLUTION FOR BUILTINS FUNCTIONS:
 *
 * - Redeclare forbidden things in the global scope, through `globals()`, using an object that will
 *   systematically throw an ExclusionError when it's called.
 * - Since those are in the global scope, they are visible through `dir()`, so add some make up on
 *   those, using a class that redefines its __qualname__ and __repr__, so that it's less obvious
 *   they are the anti-cheats (it will still remain obvious for those who know enough, but if they
 *   can find about that, they probably could solve the problem the right way anyway).
 * - The (hidden) function `__move_forward__('builtin_name')` can be used in the tests to get back the
 *   original builtin. If used, it must be done inside a closure, so that the original builtin
 *   doesn't override the "Raiser" in the global scope (see below).
 * - Pyodide runtime won't see those globals, so it is not affected in any way. Only the user's or
 *   tester's codes are.
 * - Since the hacked version are available to the user in the global runtime, they could just
 *   delete them to get back the access to the original  __builtins__ version. To limit this risk,
 *   an extra check is done after the user's code has been run, verifying that the hacked function
 *    is still defined in the global scope, and that it's still the original Raiser instance.
 *
 *
 * ## SOLUTION FOR IMPORTS
 *
 * The main problem about `import` is that it actually go directly through `__builtins__`, using
 * `__import__`. So in that case, there is no other choice than hacking directly the __builtins__,
 * and then put it back in place when not useful anymore.
 *
 *
 * ## RECURSION LIMIT
 *
 * The sys module function is directly hacked, then put back in place: meaning, the function
 * setrecursionlimit is replaced at user's runtime with a Raiser object.
 *
 * */
const setupExclusions =(excluded, recLimit)=>{
    // Store None in the __builtins___ dict for things that aren't builtin functions, aka, names
    // of forbidden module.

    /** WARNING!
     *  Keep in mind that the code of the Raiser instances will run "in context".
     *  This means it will be subject to existing exclusions, so it must never use a function that
     *  could be forbidden. Possibly...
     *  Force this reason, copies of all the builtins used in the Raiser code are stored locally,
     *  to be sure the Raiser won't use Raiser instances... XD
     * */
    const code = `
    @__builtins__.auto_run
    def _hack_exclusions_setup():

        class Raiser:
            __name__ = __qualname__ = 'function'

            def __init__(self, key):  self.key = key

            def __repr__(self): return f"<built-in function {self.key}>"

            def __call__(self, *a, **kw):
                key = self.key

                head = a and base_isinstance(a[0],base_str) and a[0].split(".")[0]

                is_forbidden = (
                    key != '__import__' or
                    key == '__import__' and head in dct
                )
                if is_forbidden:
                    that = key if key!='__import__' else head
                    ExclusionError.throw(that)

                # if reaching this point, the call is a valid import, so apply it:
                return base_import(*a,**kw)


        # Store the originals used here to avoid troubles with exclusions at runtime:
        base_import = __import__
        base_str = str
        base_isinstance = isinstance


        __builtins__.__builtins___ = dct = {}
        raiser_import = Raiser('__import__')
        dct['__import__'] = [base_import, raiser_import]
        __builtins__.__import__ = raiser_import


        glob_dct = globals()
        exclusions = ${ JSON.stringify(excluded) }
        for key in exclusions:
            stuff = getattr(__builtins__, key, None)
            dct[key] = [stuff, None]
            # => the dict will store [None,None] for module names

        if ${ recLimit } != -1:
            import sys
            sys.setrecursionlimit(${ recLimit })
            dct['setrecursionlimit'] = [sys.setrecursionlimit, None]

        for key,lst in dct.items():
            stuff = lst[0]
            if callable(stuff) and key!='__import__':       # import already handled
                glob_dct[key] = lst[1] = Raiser(key)
                # store the reference to the raiser, to check against it later

        # \`auto_run\` added for vérification purpose only, but it must stay usable:
        dct['auto_run'] = auto_run
`
    pyodide.runPython(code)
}



/**Cancel the code exclusions (done as soon as possible, to restore pyodide's normal behaviors).
 * */
const restoreOriginalFunctions = exclusions =>{
    // Don't use auto_run, in case someone messes with it...
    const code = `
def _hack_unexclude():
    dct = __builtins__.__builtins___
    G = globals() if "globals" not in dct else dct['globals']()

    # Handle special behavior of auto_run:
    key = "auto_run"
    auto_run = dct.pop(key)
    bad_auto_run = G.get(key, __builtins__.auto_run) is not auto_run
    __builtins__.auto_run = auto_run

    # Restore everything before raising anything:
    not_ok = []
    for key,(func,raiser) in dct.items():
        if key == '__import__':
            __builtins__.__import__ = func

        else:
            if raiser is not None and raiser is not G.get(key):
                not_ok.append(key)
            if func is not None:
                del G[key]  # unshadow the builtin
                if key == 'setrecursionlimit':
                    func(1000)

    if bad_auto_run:
        ExclusionError.throw("the auto_run tool...")
    if not_ok:
        ExclusionError.throw("${ exclusions }")

_hack_unexclude()
del _hack_unexclude
`
    pyodide.runPython(code)
}
