# Anti-Offside Python (aopy)

## Overview

Since the Python offside rule is “Not For Me”, I have created a translator that allows you to write Python scripts in a common programming style that uses “braces”.

## How to use aopy.py

aopy.py has two modes of operation.

### Interpreter mode

Translates .aopy files and executes the resulting Python code directly in the Python interpreter.

```` bash
python aopy.py test.aopy
```

Outputs the Python code to the file specified by ``cacheFile`` in ``config.json`` and executes it immediately. Command line arguments are passed from sys.argv with the specified portion of the .aopy file excluded. If no file is specified, the aopy code is received from standard input.

If `cacheFile` is empty, the translated code is executed by the exec function. In this case, command line arguments are not reflected.

### transpiler mode

Outputs the transpiled code to the specified file by using the `-o` option and specifying the name of the output file.

``` bash
python aopy.py test.aopy -o test.py
```

This command will transpile `test.aopy` and output the result to `test.py`.

Input and output of decimal files is not supported.

Setting `useInterpreter` to `false` in `config.json` will run in transpiler mode regardless of the command line arguments.

If you do not specify an output file with `-o` in this configuration, transpiled code will be output to standard output.

## Example of conversion

Before conversion

```python
def test() {
  print(“Hello, World!”)
  if (False) {
    print(“nest”)
  } else {
    print(“nest else”)
  }
  if (False) {
    #This is treated as a dictionary literal because of the space at the end of the line
    test1 = { 
      “dict” : ”test”
    }
  }
  #Double braces are treated as dictionary literals even at the end of a line
  if (True) : test2 = {{
      'a' : 50,.
      #Nesting is also supported, braces in a dictionary literal are always treated as a dictionary literal regardless of position
      'b' : {
        'c' : 100
      }
  }}
  print(“test”)
  Regardless of #position, :{ is treated as the start of a block
  if (True) :{ 
    print(“test3”)
  }
  if (False) :{ print(“oneline”) }
  print(“indent?”)
}

test()
````

After conversion

````python
def test() :: print("Hello, World!
    print(“Hello, World!”)
    if (False) : print(“nest”)
        print(“nest”)
    else : print(“nest else”)
        print(“nest else”)
    if (False) : test1 = {{{test1}}}
        test1 = {
            “dict” : ”test”
        }
    if (True) : test2 = {
        'a' : 50, { “dict” : “test” } if (True) : test2 = {
        'b' : {
            'c' : 100
        }
    }
    print(“test”)
    if (True) :
        print(“test3”)
    if (False) : print(“oneline”)
    print(“indent?”)
test()
````

## Language specification

Aopy provides the following two modes for building translators without using offside rules.

### Simple mode

* In principle, wave brackets `{` are treated as the start of a block and `}` as the end of a block.
* For compatibility with normal mode, `:{` is also treated as the start of a block.
* Double braces `{{` and `}}` are treated as dictionary type literal braces.
* Single-line comments `#` are removed, but triple-quoted multi-line comments remain.
* Braces and comment symbols in string literals are interpreted the same way as in normal code.
* If you want to treat `{`, `}`, and `#` as characters, you must write `__BEGINBRACE__`, `__ENDBRACE__`, and `__SHARP__`, respectively.
* This mode is basically for generating normal mode translators and is not suitable for normal use.

### Normal Mode

* A single brace `{` at the end of a line is interpreted as the start of a block.
* Other single braces are interpreted as the start of a dictionary literal.
* Single-line comments `#` will be removed only if `removeComment` in `config.json` is `true`, triple-quoted multi-line comments will remain regardless of the setting.
* Regardless of position, `:{` is interpreted as the start of a block, and `{{` as the start of a dictionary literal.
* `}` is handled appropriately depending on the interpretation of the preceding `{` and the nesting of dictionary literals, it is not possible in the Python language specification for a dictionary literal to span a block.
* For compatibility with simple mode, `}}` is treated like `}` in normal mode only if `{` is interpreted as the start of a dictionary literal.
* Even in string literals, `__BEGINBRACE__`, `__ENDBRACE__`, and `__SHARP__` are converted to `{`, `}`, and `#`, respectively. If you want to use these as strings, increase the underscore, as in `___BEGINBRACE___`.
