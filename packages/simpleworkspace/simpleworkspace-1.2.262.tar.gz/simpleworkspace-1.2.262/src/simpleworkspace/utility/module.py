import sys as _sys
import os as _os
from typing import TypeVar as _TypeVar
from types import ModuleType as _ModuleType
_T = _TypeVar('_T')


def RequireModules(*modules: str, installMissing=True):
    '''
    Checks if python modules are installed, otherwise tries to install them
    '''
    import subprocess
    from importlib.util import find_spec

    missing = []
    for module in modules:
        if find_spec(module) is None:
            missing.append(module)

    if not missing:
        return
    
    if not (installMissing):
        raise ImportError(f"Missing dependecies for this application: {missing}")
    
    print("Please wait a moment, application is missing some modules. These will be installed automatically...")
    for moduleName in missing:
        print(f"Installing {moduleName}... ", end='')
        result = subprocess.run([_sys.executable, "-m", "pip", "install", moduleName], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if(result.returncode != 0): #something went bad
            print("FAILED!")
        else:
            print("OK!")

    missing = []
    for module in modules:
        if find_spec(module) is None:
            missing.append(missing)

    if missing:
        print(f"Not all required modules could automatically be installed! Please install these modules manually: {missing}")
        raise ImportError(f"Missing dependecies for this application: {missing}")
    return

def ImportModuleDynamically(moduleName, path):
    '''
    :param moduleName: freely name the module to import
    :param path: full path to the python module
    '''
    import importlib.util

    spec = importlib.util.spec_from_file_location(moduleName, path)
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[moduleName] = mod
    _sys.path.append(_os.path.dirname(_os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return mod

def ChangeCWDToMainModule():
    '''Set the directory of the main script module as the current working directory'''
    _os.chdir(ModuleInfo.Factory_MainModule().pathInfo.Tail)

class ModuleInfo:
    '''
    A wrapper class for retrieving information about a module
    
    :Examples:
    >>> ModuleInfo(sys.modules[__name__]) # Wraps current module
    '''

    def __init__(self, module:_ModuleType):
        '''
        :param module: The module to retrieve information from.
        '''

        from simpleworkspace.io.path import PathInfo

        self.module = module
        '''The raw module object that is wrapped'''
        self.pathInfo = PathInfo(module.__file__)
        '''
            >>> pathInfo.Absolute # '/path/to/main_script.py'
            >>> pathInfo.Head     # 'main_script.py'
            >>> pathInfo.Tail     # '/path/to'
        '''

    def GetDeclaredClasses(self, targetClass: type[_T], includeChildsOnly=False) -> dict[str, type[_T]]:
        '''
        Get the classes declared in the module that are subclasses of the specified target class and the target class itself.

        :param targetClass: The target class to search for.
        :param includeChildsOnly: If True, include only child classes of the target class, aka exclude targetClass itself
        :return: A dictionary containing the matched class names as keys and class objects as values.
        '''
        import inspect

        matchedClasses = {}
        for className, classObj in inspect.getmembers(self.module, inspect.isclass):
            if(self.module.__name__ != classObj.__module__):
                continue
            if(not issubclass(classObj, targetClass)):
                continue
            if(includeChildsOnly) and (classObj == targetClass):
                continue

            matchedClasses[className] = classObj
        
        return matchedClasses
    
    def GetDeclaredFunctions(self):
        '''
        Gets all the declared methods in a module

        :return: A dictionary containing function name as keys and function object as values.
        '''
        import inspect

        funcs = {}
        for funcName, funcObj in inspect.getmembers(self.module, predicate=inspect.isfunction):
            if(self.module.__name__ != funcObj.__module__):
                continue
            funcs[funcName] = funcObj
        return funcs
    
    def __eq__(self, __value: object) -> bool:
        if(isinstance(__value, ModuleInfo)):
            return self.module == __value.module
        return False
    
    @classmethod
    def Factory_MainModule(cls):
        return cls(_sys.modules["__main__"])
    