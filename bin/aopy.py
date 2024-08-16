import os
import sys
import fileinput
import subprocess
import json
import importlib

# Reading JSON config file
config = {}
readed = False
def aopyReadConfig(): return readConfigStart() if readed == False else 0
def readConfigStart(): global readed; global config; config = mapDict(thisScriptDir() + 'config.json'); readed = True; return 0
def readJson(file): return json.load(open(file, 'r', encoding='UTF-8'))
def assignKeys(src, dst, key): dst[key] = src[key]['value'] if 'value' in src[key] else errorExit('Broken config file.')
def objCheck(obj): True if isinstance(obj, dict) else errorExit('Broken config file.')
def mapDict(file): obj = readJson(file); objCheck(obj); result = {}; list(map(lambda key: assignKeys(obj, result, key), obj.keys())); return result
def aopyGetConfig(name): return config[name] if name in config else errorExit('No config value: ' + name)
def getConfigDict(): return config
def setConfigDict(value): global config; config = value

# aopy symbol translate functions
def convertSymbol(line): return convertSymbolEscape(line.replace('__BEGINBRACE__', '{').replace('__ENDBRACE__', '}').replace('__SHARP__', '#'))
def convertSymbolEscape(line): return line.replace('_{_', '__BEGINBRACE__').replace('_}_', '__ENDBRACE__').replace('_#_', '__SHARP__')

# aopy translater(Simple mode)
indent = 0
def convertPreprocess(line): return line.replace('{{', '__BEGINBRACE__').replace('}}', '__ENDBRACE__').replace('\n', '')
def isEnd(line): global indent; indent -= 1 if line.find('}') != -1 else 0
def delComment(line): return line.split('#')[0]
def convertBrace(line): return line.replace(':{', ':').replace('{', ':').replace('}', '')
def setLine(line): return ' ' * aopyGetConfig('indentLength') * indent + convertBrace(delComment(line)).strip()
def checkBlank(line): return line if line.strip() != '' else ''
def isBegin(line): global indent; indent += 1 if line.find('{') != -1 else 0
def translate(line): line = convertPreprocess(line); isEnd(line); result = checkBlank(convertSymbol(setLine(line))); isBegin(line); return result

# Read script functions
def aopyRead(func, file, rblank): return '\n'.join(list(filter(lambda line: rblank == False or line != '', list(map(func, fileinput.input(file, encoding='utf-8'))))))
def aopyReadString(func, code, rblank): return '\n'.join(list(filter(lambda line: rblank == False or line != '', list(map(func, code.split('\n'))))))

# Write script fuctions
def aopyFileCheck(file): return sys.stdout if file == 'stdout' else open(file, 'w', encoding='utf-8')
def aopyWrite(code, file): fp = aopyFileCheck(file); fp.write(code); fp.close(); return 0

# Platform dependent functions
def getPythonPlatform(): return 'python' if sys.platform.startswith('win') else 'python3'
def getPythonConfig(): pycom = aopyGetConfig('pythonCommand'); return getPythonPlatform() if pycom == '' else pycom

# Code execution functions
aopyScriptDir = None
def getScriptFileDir(file): return os.path.dirname(os.path.realpath(file)) + os.sep if file != None else None
def aopyExec(code): cacheFile = aopyGetConfig('cacheFile'); return aopyExecString(code) if cacheFile == '' else aopyExecFile(code, aopyScriptDir + cacheFile)
def aopyExecString(code): exec(code); return 0
def aopyExecFile(code, file): aopyWrite(code, file); proc = subprocess.run([getPythonConfig(), file] + sys.argv[2:]); os.remove(file); return proc.returncode

# Invoking Normal mode transpiler
def getModuleName(file): return os.path.splitext(os.path.basename(file))[0]
def loadTranspiler(): return importlib.import_module(getModuleName(getTranspilerAopyFile()))
def aopyTranspile(code): aopyReadConfig(); return aopyReadString(loadTranspiler().transpile, code, aopyGetConfig('removeBlankLine'))

# Loading normal mode transpiler and initialize functions
def aopyExecOrTranspile(code, file): aopyWrite(code, file) if file != '' else aopyExec(code)
def aopyTranspileArgCheck(): return sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '-o' else aopyInterpModeCheck()
def aopyInterpModeCheck(): interp = aopyGetConfig('useInterpreter'); return '' if interp == True else 'stdout'
def getTranspilerAopyFile(): return thisScriptDir() + aopyGetConfig('transpilerFile')
def getTranslatedAopyFile(): return getTranspilerAopyFile().replace('.aopy', '.py')
def translateAopyFile(): aopyWrite(aopyRead(translate, getTranspilerAopyFile(), True), getTranslatedAopyFile()); return getTranslatedAopyFile()
def getAopyTranspiler(): return getTranslatedAopyFile() if os.path.isfile(getTranslatedAopyFile()) else translateAopyFile()
def execTranspiler(): return subprocess.run([getPythonConfig(), getAopyTranspiler()] + sys.argv[1:]).returncode
def setAopyEnvPath(): env = os.environ.copy(); env['PYTHONPATH'] = thisScriptDir() + os.pathsep + env['PYTHONPATH'] if 'PYTHONPATH' in env else thisScriptDir(); return env
def setAopyPath(): os.environ.update(setAopyEnvPath()); return 0
def aopyInitialize(): setAopyPath(); aopyReadConfig(); return execTranspiler()

# Aopy initialization functions
def aopyReadFileCheck(file): return file if os.path.isfile(file) and os.access(file, os.R_OK) else errorExit('Script not found: ' + file)
def aopyReadFileArgCheck(): return aopyReadFileCheck(sys.argv[1]) if len(sys.argv) > 1 else None
def aopyInputArgCheck(): return sys.argv[1] if aopyReadFileArgCheck() else None
def aopySetScriptDir(): global aopyScriptDir; result = aopyInputArgCheck(); aopyScriptDir = getScriptFileDir(result); return result
def aopyStart(func): aopyReadConfig(); code = aopyRead(func, aopySetScriptDir(), aopyGetConfig('removeBlankLine')); aopyExecOrTranspile(code, aopyTranspileArgCheck()); return 0

# Misc utility functions
def errorExit(mes) : print(mes); sys.exit(1)
def thisScriptDir() : return os.path.dirname(os.path.realpath(__file__)) + os.sep

# main function
if __name__ == '__main__': sys.exit(aopyInitialize())
