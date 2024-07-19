# aridity
DRY config and template system, easily extensible with Python

## The Arid Manifesto
* Keys are paths to avoid concatenation
* It's never necessary to repeat a value
* Minimal syntax for surprise-free authoring
* Evaluation lazy and influenced by context
* Strongly (dynamically) typed values
* Central defaulting rather than at call sites
* Templating using same syntax as expressions
* Easy to correctly quote/escape values in templates
* Extensibility via user-defined functions
* Easy tasks are easy, hard tasks are possible
* Many applications can share one user config
* Principle of least astonishment driven design
* Don't make users jump through hoops

## Motivation
* Environment variables are too crude to configure non-trivial apps, and maybe even trivial apps in the cloud
    * They do not support nested data or lists, without some encoding scheme implemented in app code or a lib
    * Multiple bespoke encoding schemes in the system are an error-prone maintenance burden worth avoiding
* Testing code that queries the environment directly comes with a big risk of leaking state between tests
* Often tools/libraries must be configured using config files
    * Support for config file interpolation is not enough to stay DRY, and comes with a different set of gotchas per tool
    * In particular Helm/Terraform have their own ways of sharing config between envs
* aridity is a general purpose solution for all the above, also see [soak](https://pypi.org/project/soak/)

## Config API
* Normally you pass around a Config object, and application code can get data out via attribute access e.g. config.foo.bar
    * Here config.foo is also a Config object, a child scope of config named foo
    * The passing around can be taken care of by a dependency injection container such as [diapyr](https://pypi.org/project/diapyr/)
* Every Config has an associated ConfigCtrl on which Python API such as processtemplate is available
    * Use negation to get ConfigCtrl when you have a Config e.g. (-config).processtemplate(...)
    * Use the node attribute to get Config when you have a ConfigCtrl, this is a rare situation in practice
* When unit testing a class or function that expects a Config object, you can use SimpleNamespace to mock one

## Guidelines
* Config files have the extension .arid and templates .aridt
* A template is simply a file-sized aridity expression
    * Conventionally the template processor sets " to the appropriate quote function for the file format, e.g. jsonquote for JSON/YAML
* Instead of adding Python objects to the config in main, it's tidier to use aridity's pyref function to achieve this
* When some value needs to be constructed using concatenation, consider whether it would be more tasteful to do this in the config

## Feature switch
* Sometimes we want to deploy a change, but something in production isn't ready for that change
* A feature switch allows deployment to production in this case
* Add a boolean to the base config (conventionally root.arid) e.g. foo enabled = true
    * This value should be the configuration that we eventually want in all environments
* In production config, override with foo enabled = false
* In the code, read config.foo.enabled and enable the change based on this boolean
* The above can now be deployed to all environments, and is not a blocker for other changes
* Later when production is ready for it, it's a 1 line change to remove the override from production config

## Config file syntax
```
: Until aridity gets support for comments, you can use the colon directive to ignore data.
: Directives MUST be separated from data by whitespace, and are typically punctuation.

: Here's the equals directive:
foo = bar
: This does what you'd expect - assign the string value bar to foo.
: Observe that bar isn't quoted, values in aridity are normally barewords.
: foo is actually a path of length 1, path components are whitespace-separated:
this is a path = this is a value
: Any existing assignment can be overridden:
foo = baz
this is a path = this is different

: Internal whitespace in values is preserved (leading and trailing whitespace is not):
two sentences = Some like 2 spaces.  After a full stop.

: You can use indentation to avoid typing a common path prefix multiple times:
app1 feature1
    data1 = value1
    data2 = value2
app2
    feature1 data = value3
    feature2
        data1 = value4
        data2 = value5
: Exactly the same effect without using indentation:
app1 feature1 data1 = value1
app1 feature1 data2 = value2
app2 feature1 data = value3
app2 feature2 data1 = value4
app2 feature2 data2 = value5

: The right hand side of an equals is actually an expression.
: In an expression, a dollar sign with brackets can be used to refer to another path:
has value
    bar = $(foo)
    value3 = $(app2 feature1 data)
: Round brackets and square brackets have exactly the same effect:
also has value bar = $[foo]
: Values can be concatenated:
two bars
    without spacing = $(foo)$(foo)
    with one space  = $(foo) $(foo)
    with 2 spaces   = $(foo)  $(foo)
: A few paths are predefined in every new context, such as:
home directory = $(~)

: To get a literal dollar there is a special form for quoting:
financial report = $'(We lost $100 on Friday.)
: Unlike in older versions, nested brackets (if any) do not end the special form early:
behaviour
    expected = $'[Lunch cost $20 (worth it though).]
    same     = $'(Lunch cost $20 (worth it though).)
: Consequently, unbalanced brackets of the same kind as used by the special form must be avoided:
interval
    lower = $'[The interval ][$'[0, 1) includes 0 but not 1.]
    upper = $'(The interval )($'(0, 1] includes 1 but not 0.)

: Another special form can be used to preserve leading/trailing whitespace:
padded bars = $.( $(foo) $(foo) )
: Brackets can span multiple lines:
bar per line
    without final newline = $.($(foo)
$(foo))
    with final newline = $.($(foo)
$(foo)
)

: Evaluation is lazy, the expression is what is actually (and eagerly) assigned to the path:
no problem = $(this path will get a value later)
: If your use-case demands it, you can force eager evaluation:
bar even if foo changes later := $(foo)

: When evaluating a path the local scope is examined first, then its parents if path not found:
host
    short path = nope
    guest short path = yep
    should be nope = $(short path)
    guest should be yep = $(short path)
does not work = $(short path)

: Use the dot directive to include config from another file:
. /path/to/other/config.arid
: Thus you can factor out any config that's common to multiple deployments, and override as needed.
: It's possible (but maybe not so useful) to include under a non-trivial path:
other stuff . /path/to/other/config.arid
: There is no default context for relative paths, you must set cwd up-front as inclusion is not lazy:
cwd = /path/to
. other/config.arid

: Text between dollar and open bracket (that isn't a special form) is a function name.
: A useful function predefined in every new context is the platform slash:
path = $/($(~) Desktop report.txt)
: Unlike most functions, / can also be used (less legibly) as a value:
path = $(~)$(/)Desktop$(/)report.txt
: All functions are first class objects that can be assigned and overridden in the usual ways:
slash := $(/)
/ = something else
path = $slash($(~) Desktop report.txt)

: Simple lists can be created using the plus equals convenience directive.
: Indentation means you don't have to repeat the directive for every list element:
years +=
    2018
    2019
years += 2020
: A predefined join function takes a list and a separator and does what you'd expect:
copyright = $join($(years) $.(, ))
: Observe that functions typically take values not identifiers, so you have to 'get' explicitly.
: Lists are just a special case of nested scopes, which are much more powerful:
person
    $.(The Guardians) year = 2018
    Greta year = 2019
summary = Person of the Year was $join($map($(person) $.($label() in $(year))) $.(, )).
: Here the predefined label function gives you access to the last path component of a list element.
```

## Templates
* A template is simply an expression in a file, that may be quite large
* These are typically used to create config files for other languages e.g. YAML, HCL
    * Note that literal dollar signs must be quoted as above, everything else is safe
* A processtemplate script is provided for basic processing
```
processtemplate app.json.aridt <config.arid >app.json
```
* Conventionally the `"` path is set to the most useful escape function for the target format
    * Brackets can be elided in function composition e.g. `$"$(key)` is the same as `$"($(key))`

## Commands

### arid-config
Print given config (with optional path in config) as shell snippet.

### aridity
Interactive REPL.

### processtemplate
Process the given template to stdout using config from stdin.

## API

<a id="aridity.config"></a>

### aridity.config

<a id="aridity.config.ForeignScopeException"></a>

#### ForeignScopeException Objects

```python
class ForeignScopeException(Exception)
```

The operation required a scope at precisely the given path.

<a id="aridity.config.ConfigCtrl"></a>

#### ConfigCtrl Objects

```python
class ConfigCtrl()
```

High level scope API.

<a id="aridity.config.ConfigCtrl.r"></a>

###### r

```python
@property
def r()
```

Get config object for reading, i.e. missing scopes will error.

<a id="aridity.config.ConfigCtrl.w"></a>

###### w

```python
@property
def w()
```

Get config object for writing, i.e. missing scopes will be created.

<a id="aridity.config.ConfigCtrl.loadappconfig"></a>

###### loadappconfig

```python
def loadappconfig(mainfunction,
                  moduleresource,
                  encoding='ascii',
                  settingsoptional=False)
```

Using app name as prefix load config from the given resource, apply user settings, and return config object for app. Context module for loading resource and the app name are deduced from `mainfunction`, or these can be provided as a tuple. Set `settingsoptional` to suppress the usual error if ~/.settings.arid does not exist.

<a id="aridity.config.ConfigCtrl.load"></a>

###### load

```python
def load(pathorstream)
```

Execute config from the given path or stream.

<a id="aridity.config.ConfigCtrl.execute"></a>

###### execute

```python
def execute(text)
```

Execute given config text.

<a id="aridity.config.ConfigCtrl.__iter__"></a>

###### \_\_iter\_\_

```python
def __iter__()
```

Yield keys and values.

<a id="aridity.config.ConfigCtrl.processtemplate"></a>

###### processtemplate

```python
def processtemplate(frompathorstream, topathorstream)
```

Evaluate expression from path/stream and write result to path/stream.

<a id="aridity.config.RConfig"></a>

#### RConfig Objects

```python
class RConfig(Parabject)
```

<a id="aridity.config.RConfig.__iter__"></a>

###### \_\_iter\_\_

```python
def __iter__()
```

Yield values only. Iterate over `-self` for keys and values.

<a id="aridity.directives"></a>

### aridity.directives

<a id="aridity.directives.Colon"></a>

#### Colon Objects

```python
@_directive
class Colon()
```

Ignore rest of logical line.

<a id="aridity.directives.Source"></a>

#### Source Objects

```python
@_directive
class Source()
```

Include path or resource at prefix.

<a id="aridity.directives.Equals"></a>

#### Equals Objects

```python
@_directive
class Equals()
```

Assign expression to path.

<a id="aridity.directives.ColonEquals"></a>

#### ColonEquals Objects

```python
@_directive
class ColonEquals()
```

Evaluate expression and assign result to path.

<a id="aridity.directives.PlusEquals"></a>

#### PlusEquals Objects

```python
@_directive
class PlusEquals()
```

Assign expression to prefix plus an opaque key, i.e. add to list.

<a id="aridity.functions"></a>

### aridity.functions

<a id="aridity.functions.Functions"></a>

#### Functions Objects

```python
class Functions()
```

<a id="aridity.functions.Functions.screenstr"></a>

###### screenstr

```python
def screenstr(scope, resolvable)
```

GNU Screen string literal.

<a id="aridity.functions.Functions.scstr"></a>

###### scstr

```python
def scstr(scope, resolvable)
```

SuperCollider string literal.

<a id="aridity.functions.Functions.hclstr"></a>

###### hclstr

```python
def hclstr(scope, resolvable)
```

HashiCorp configuration language string literal.

<a id="aridity.functions.Functions.groovystr"></a>

###### groovystr

```python
def groovystr(scope, resolvable)
```

Groovy string literal.

<a id="aridity.functions.Functions.pystr"></a>

###### pystr

```python
def pystr(scope, resolvable)
```

Python literal.

<a id="aridity.functions.Functions.shstr"></a>

###### shstr

```python
def shstr(scope, resolvable)
```

Shell string literal.

<a id="aridity.functions.Functions.jsonquote"></a>

###### jsonquote

```python
def jsonquote(scope, resolvable)
```

JSON literal, also suitable for YAML.

<a id="aridity.functions.Functions.xmlattr"></a>

###### xmlattr

```python
def xmlattr(scope, resolvable)
```

XML attribute literal (including quotes).

<a id="aridity.functions.Functions.xmltext"></a>

###### xmltext

```python
def xmltext(scope, resolvable)
```

XML content, suggest assigning this to & with xmlattr assigned to " as is convention.

<a id="aridity.functions.Functions.tomlquote"></a>

###### tomlquote

```python
def tomlquote(scope, resolvable)
```

TOML string literal.

<a id="aridity.functions.Functions.urlquote"></a>

###### urlquote

```python
def urlquote(scope, resolvable)
```

Percent-encode all reserved characters.

<a id="aridity.functions.Functions.map"></a>

###### map

```python
def map(scope, objsresolvable, *args)
```

If given 1 arg, evaluate it against every scope in `objsresolvable` and return that list.
If given 2 args, the first is a variable name to which each scope is temporarily assigned.
If given 3 args, the first two are variable names for scope key and scope respectively.

<a id="aridity.functions.Functions.join"></a>

###### join

```python
def join(scope, resolvables, *args)
```

Concatenate the given list, using optional separator. Frequently used with `map`.

<a id="aridity.functions.Functions.str"></a>

###### str

```python
def str(scope, resolvable)
```

Coerce to string.

<a id="aridity.functions.Functions.list"></a>

###### list

```python
def list(scope, *resolvables)
```

Create a list.

<a id="aridity.functions.Functions.try_"></a>

###### try\_

```python
@realname('try')
def try_(scope, *resolvables)
```

Attempt to evaluate each resolvable, returning the first that succeeds.

<a id="aridity.functions.Functions.hereslash"></a>

###### hereslash

```python
@realname('./')
def hereslash(scope, *resolvables)
```

Join the given path components with the directory of the current resource.

<a id="aridity.functions.Functions.readfile"></a>

###### readfile

```python
def readfile(scope, resolvable)
```

Include the content of the given path.

<a id="aridity.functions.Functions.processtemplate"></a>

###### processtemplate

```python
def processtemplate(scope, resolvable)
```

Evaluate the content of the given path as an expression.

<a id="aridity.functions.Functions.pyref"></a>

###### pyref

```python
def pyref(scope, moduleresolvable, qualnameresolvable)
```

Python object in given module with given qualified name. Module may be relative to current resource, in which case assignment with `:=` is normally necessary. Typically used to import functions.

<a id="aridity.functions.Functions.pyres"></a>

###### pyres

```python
def pyres(scope, packageresolvable, nameresolvable)
```

Python resource for inclusion with `.` directive.

<a id="aridity.grammar"></a>

### aridity.grammar

<a id="aridity.keyring"></a>

### aridity.keyring

<a id="aridity.keyring.gpg"></a>

###### gpg

```python
def gpg(scope, resolvable)
```

Use gpg to decrypt the given base64-encoded blob.

<a id="aridity.model"></a>

### aridity.model

<a id="aridity.model.Resolvable"></a>

#### Resolvable Objects

```python
class Resolvable(Struct)
```

<a id="aridity.model.Resolvable.resolve"></a>

###### resolve

```python
def resolve(scope)
```

Evaluate this expression against the given scope.

<a id="aridity.model.wrap"></a>

###### wrap

```python
def wrap(value)
```

Attempt to wrap the given value in a model object of the most specific type.

<a id="aridity.scope"></a>

### aridity.scope

<a id="aridity.scope.AbstractScope"></a>

#### AbstractScope Objects

```python
class AbstractScope(Resolvable)
```

<a id="aridity.scope.AbstractScope.resolved"></a>

###### resolved

```python
def resolved(*path, **kwargs)
```

Follow the given path to get an expression, evaluate it (resolving any paths it requires, recursively), and return the resulting model object.

<a id="aridity.scope.Slash"></a>

#### Slash Objects

```python
class Slash(Text, Function)
```

As text, the platform slash. As function, join args using that slash, starting with the last absolute path (or using all args if all relative).

<a id="aridity.util"></a>

### aridity.util

<a id="aridity.util.openresource"></a>

###### openresource

```python
def openresource(package_or_name, resource_name, encoding='ascii')
```

Like `pkg_resources.resource_stream` but text mode.

<a id="aridity.util.solo"></a>

###### solo

```python
def solo(v)
```

Assert exactly one object in the given sequence and return it.

<a id="parabject"></a>

### parabject

<a id="parabject.register"></a>

###### register

```python
def register(obj, parabject)
```

Set `obj` to be the regular object associated with the given parabject.

<a id="parabject.dereference"></a>

###### dereference

```python
def dereference(parabject)
```

Get the regular object associated with `parabject` or raise UnknownParabjectException.

<a id="parabject.Parabject"></a>

#### Parabject Objects

```python
class Parabject(object)
```

Subclasses typically implement `__getattr__` for dynamic behaviour on attribute access.

<a id="parabject.Parabject.__neg__"></a>

###### \_\_neg\_\_

```python
def __neg__()
```

Dereference this parabject.

