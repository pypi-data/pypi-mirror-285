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



class Ctx {

  static BASE_CTX = {
    skipped: false,
    success: true,                // false if error, not if skipped

    err: null,                    // Error instance
    stdErr: "",                   // Error as string (msg to output, formatted)
    isAssertErr:false,
    stdout: "",
    running: "<unknown>",         // Informational purpose

    useIO: true,                  // Apply setup/teardown? (without consideration of use)
    keepRunningOnAssert: false,   // If true, consider the section ran successfully on AssertionError (this is env related)
    isEnvSection: true,           // Any of env, env_term, ... => "not user code or cmd"
    applyExclusionsIfAny: false,  // Apply exclusions specifically on this run (if any). Note: `!isEnvSection` is not specific enough!
    section: "<unknown>",
    archiveSuccess: false,        // If true, the section will be registered as ran successfully (if it is so). To use on the last action of the section.
    method: ()=>null,             // Runner method to... run when everything is ready
    code: ".",                    // If empty string, the Runner method won't ever be called. Default is not empty, because some Runner won't need to pass `code` to the ctx to know what to do (or the code needed is not known yet: Features)
    methodArgs: [],
    logConfig: {},
  }


  static with(ctx, runtime){
    let section = ctx.section || Ctx.BASE_CTX.section
    if(!ctx) ctx={}         // no argument

    else if(typeof(ctx)=='string'){   // environment name only
      section = ctx
      ctx = {
        code:                runtime.runner[`${ section }Content`].trim(),
        archiveSuccess:      true,     // always on Environment codes
        keepRunningOnAssert: section.startsWith('env'),
        method:              runtime.runner.installImportsAndRunEnvCode,
      }
    }

    return {
      running: `${ ctx.section || '?' }_${ ctx.method.name }`,
      ...Ctx.BASE_CTX,
      ...ctx,
      section,
    }
  }
}




/**Manage the environment when in need to execute some code in pyodide.
 *
 * Holds all the logic to manage all the possible outcomes:
 * Used as "throw away" data structure, once the full user action is done: this allows to mutate
 * all that one needs, being sure it wont affect the original data in the (PythonSectionsRunner).
 * */
class RuntimeManager {

  constructor(runner){
    this.runner = runner

    // --- Python logistic related ---
    this.excluded        = runner.excluded
    this.excludedMethods = runner.excludedMethods
    this.recLimit        = runner.recLimit
    this.whiteList       = runner.whiteList
    this.autoLogAssert   = true               // default for the PUBLIC tests...
    this.purgeStackTrace = false              // default for the PUBLIC tests...
    this.withStdOut      = true               // default for the PUBLIC tests...
    this.packagesAliases = {                  // useless so far...
      // turtle: "pyo_js_turtle",             // This never got finished => unusable.
    },
    // --- Runtime logistic related ---
    this.stdErr          = ""                 // First encountered error message
    this.finalMsg        = CONFIG.lang.successMsg.msg
    this.isAssertErr     = false              // is the error an assertion error
    this.ran             = {start:1}          // keep track of the successfully run env sections (or raising assertion errors)
    this.dependencies    ={
      env:      'start',
      envTerm:  'env',
      code:     'env',        // actually not used as a condition for now
      cmd:      'envTerm',    // actually not used as a condition for now
      postTerm: 'envTerm',
      post:     'env',
    }
    this.gotBigFail = false   // If true, new errors won't replace the current one
  }

  get stopped(){ return Boolean(this.stdErr) }

  changeDependency(source, target){
    if(this.dependencies[source]===undefined){
      throw new Error("Invalid source dependency: " + source)
    }
    this.dependencies[source] = target
  }

  cleanup(){ return this.runner = this.runCodeAsync = null }


  stillRunnable(ctx){
    const outcome = ctx.isEnvSection
                  ? ctx.code && this.ran[ this.dependencies[ctx.section] ]
                  : ctx.code && !this.stopped
    return outcome && !this.gotBigFail
  }



  /**Run on Runner method (async), surrounding it with all necessary logics, like:
   *
   *    - setup+teardown stdout
   *    - setup+teardown exclusions
   *    - give feedback
   *    - try/catch where appropriate (handling properly the exclusions removal case)
   *
   * This method should never actually throw, except in "BigFail" cases.
   * It uses a ctx object, which holds the local executions data, and will merge the data
   * when appropriate in the RunnerManager (which holds runtime information for the current
   * user's action).
   *
   * Inside this "runWithCtx" call, subsequent methods calls are skipped if an error has been
   * registered in the @ctx object, unless the method is specified as "should `always` happen"
   *
   * Note: NOT in this.stdErr, which is more global, while the current run could involve `post`
   *       actions that should potentially occur even if an error has already occur previously
   *       in the current user's action.
   * */
  async runWithCtx(ctx){
    ctx = Ctx.with(ctx, this)

    if(!this.stillRunnable(ctx)){
      jsLogger('[Runtime] - SKIPPED')
      ctx.skipped = true
      return ctx
    }

    jsLogger('[Runtime] - running ', ctx.running)
    // No need for error extra handling: big fails handled in lockedRunnerWithBigFailWarningFactory

    await this._runCaught( ctx, this.setupManager)
    await this._runCaught( ctx, this.applyRunnerMethod)
    await this._runCaught( ctx, this.removeExclusions, {always:true})
    await this._runCaught( ctx, this.teardownManager,  {always:true, critical:true})

    this.runner.giveFeedback(ctx.stdout, ctx.stdErr)
    if(ctx.archiveSuccess){
      this.ran[ctx.section] = ctx.success
    }
    return ctx
  }





  needExclusions(ctx){
    return ctx.applyExclusionsIfAny
        && (this.excluded.length>0 || this.recLimit > 0)
  }




  /**1. Put the StringIO object in place if needed (stdout extraction).
   * 1. If the method to run is asking for excluions "environment-related", STOP HERE.
   * 1. OTHERWISE, if the ctx is asking for exclusions applications:
   *     1. Put in place exclusions if any
   *     1. Cleanup pyodide environment (`auto_run.clean`)
   * */
  async setupManager(ctx){
    if(ctx.useIO) setupStdIO()

    if(ctx.isEnvSection) return;

    if(this.needExclusions(ctx)){
      jsLogger('[checkPoint] - running - setup exclusions')
      setupExclusions(this.excluded, this.recLimit)
    }
    pyodideCleaner()
  }


  /**Run the desired Runner method, once all the setup has been managed.
   * If it succeeds (aka, the method doesn't throw any error), the ctx is marked as successful.
   *
   * The Runner method is supposed to take this kind of signature:
   *
   *      method(...ctx.methodArgs, ctx, runtime)
   *
   * Where `ctx.methodArgs` are arguments the RuntimeManager cannot know about in the first place.
   * The two last arguments are always passed but may be ignored on the actual method signature, if
   * it doesn't make use of them.
   * */
  async applyRunnerMethod(ctx){
    jsLogger('[checkPoint] - running method runner -', ctx.running)
    await ctx.method.call(this.runner, ...ctx.methodArgs, ctx, this) // always send extras args (in case useful)
    ctx.success = true
  }


  /**Remove the exclusions.
   * WARNING:     1. Could raise ExclusionError!
   *              2. Must be _absolutely sure_ that they are removed, even if the user's code
   *                 already raised (or the tests)...
   * */
  async removeExclusions(ctx){
    if(this.needExclusions(ctx)){
      jsLogger('[checkPoint] - running - removing exclusions')
      restoreOriginalFunctions(this.excluded)
    }
  }


  async teardownManager(ctx){
    let stdout = ctx.useIO ? getFullStdIO() : ""
    if(!this.withStdOut) stdout = ''
    else if(!ctx.isEnvSection) stdout = textShortener(stdout)
    ctx.stdout = stdout

    this.handleError(ctx)
  }




  /**In case an error has been registered in @param {, } ctx  */
  handleError(ctx, replLogConf=null){
    if(!ctx.err) return;

    this.finalMsg = ""

    ;[ctx.stdErr, ctx.isAssertErr] = generateErrorLog(ctx.err, replLogConf || ctx.logConfig)

    // If ever multiple errors happen, an assertion error will always be the very
    // first one, so always keep if any (avoid the need to condition the update)
    if(!this.gotBigFail){
      this.isAssertErr ||= ctx.isAssertErr
      this.stdErr        = ctx.stdErr
    }
    ctx.success = ctx.keepRunningOnAssert && ctx.isAssertErr
  }


  async _runCaught(ctx, method, conf={}){
    if(ctx.err && !conf.always) return
    try{
      await method.call(this, ctx)
    }catch(e){
      jsLogger('[Runtime] - ERROR ', ctx.method.name, ctx.running)
      ctx.err = e
      if(conf.critical) throw e
    }
  }
}
