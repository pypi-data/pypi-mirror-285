from abc import ABC as _ABC, abstractmethod as _abstractmethod
import os as _os
import json as _json
from typing import Generic as _Generic, TypeVar as _TypeVar, Any as _Any, Type as _Type

_T = _TypeVar("_T")

class SettingsTemplate():
    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self): #iters keys
        return iter(self.__dict__)
    
    def __len__(self): #count key value pairs
        return len(self.__dict__)


class _SettingsManager_Base(_ABC, _Generic[_T]):
    '''
    Abstract Settingsmanager that supports dynamic and strongly typed settings
        * Uses dynamic settings management by default when no templates are provided
        * For strongly typed settings with defaultable settings, supply a derived SettingsTemplate as the generic Type and constructor arg

    Example Usage, Dynamic settings:
    >>> manager = SettingsManager_JSON('./tmp.json')
        manager.LoadSettings()
        if("key1" in manager.Settings):
            val1 = manager.Settings["key1"]
        manager.Settings["key1"] = 10
        manager.SaveSettings()

    Example Usage, Typed settings:
    >>> class MyTemplate(SettingsTemplate):
            def __init__(self):
                self.val1:str = "hej" #both typehint and default value
                self.val2:str = None
        #generic type gives intellisense, type arg creates default values
        manager = SettingsManager_JSON('./tmp.json', MyTemplate)
        manager.LoadSettings()
        if(manager.Settings.val1 is not None):
            val1 = manager.Settings.val1
        manager.Settings.val1 = 10
        manager.SaveSettings()
    '''
    def __init__(self, settingsPath:str, settingsTemplate: _Type[_T] = SettingsTemplate):
        self._settingsPath = settingsPath
        if(not isinstance(settingsTemplate, type)):
            raise TypeError(f"SettingsTemplate needs to be a class type, got {type(settingsTemplate)}")
        
        self._settings: _T = settingsTemplate()

    @property
    def Settings(self):
        return self._settings
    
    @Settings.setter
    def Settings(self, value:object|dict):
        if(isinstance(value, dict)): #dict has no __dict__ property therefore special scenario
            self.Settings.__dict__ = value
        else:
            self.Settings.__dict__ = value.__dict__

    @_abstractmethod
    def _ParseSettingsFile(self, filepath) -> dict[str, _Any]:
        '''responsible for parsing setting file and returning a settings object'''

    @_abstractmethod
    def _ExportSettingsFile(self, settingsObject: dict[str, _Any], outputPath: str):
        '''responsible for saving the settingsObject to file location in self._settingsPath'''
  
    def ClearSettings(self):
        self.Settings = type(self.Settings)()

    def LoadSettings(self):
        '''Loads the setting file from specified location to the memory at self.settings'''
        self.ClearSettings()
        if not (_os.path.exists(self._settingsPath)):
            return

        settingsObject = self._ParseSettingsFile(self._settingsPath)
        #instead of replacing all the settings, we set it to default state, and copy over keys
        #incase default settings are specified/overriden, even if only one of the default setting existed in the file
        #we will keep other default settings as specified and only change value of new settings parsed
        self.Settings.__dict__.update(settingsObject) 
        return

    def SaveSettings(self):
        self._ExportSettingsFile(self.Settings.__dict__, self._settingsPath)


class SettingsManager_JSON(_SettingsManager_Base[_T]):
    def _ParseSettingsFile(self, filepath):
        with open(filepath, mode='r') as fp:
            return _json.load(fp)

    def _ExportSettingsFile(self, settingsObject, outputPath):
        with open(outputPath, mode='w') as fp:
            _json.dump(settingsObject, fp)
        return

class SettingsManager_BasicConfig(_SettingsManager_Base[_T]):
    '''
        Basic Config files are the simplest form of KeyValuePair config files.
        * each line consists of "key=value" pair.
        * comments can be placed anywhere with '#' both at start of a line or inline after a setting
        * whitespaces are trimmed from start and end of both key and the value. "key=value" is same as " key = value "
        * This parser is intentionally not compatible with INI format (will throw an exception only if a section is detected).
          The reason behind this is that basic config files don't use sections and therefore rely that every setting key is 
          unique. An INI file on the other hand can have same setting key under different sections.
    '''

    _fileLineOrdering = [] #tracks positions of lines to be able to preserve comments
    _fileLineOrderCounter = 0
    
    def _AddFileLineOrder(self, data, type):
        self._fileLineOrdering.append((self._fileLineOrderCounter, data, type)) #indexes: 0 = order, 1 = data, 2 = type of data
        self._fileLineOrderCounter += 1
    
    def _ResetFileLineOrder(self):
        self._fileLineOrdering = []
        self._fileLineOrderCounter = 0

    def _ParseSettingsFile(self, filepath):
        self._ResetFileLineOrder()
        conf = {}
        with open(filepath) as fp:
            for lineNo, line in enumerate(fp, start=1):
                line = line.strip()

                if line == '': #only a blank line
                    self._AddFileLineOrder(None, None)
                    continue
                elif line.startswith('#'): #only a comment line
                    self._AddFileLineOrder(line, "comment")
                    continue

                keyValueAndComment = line.split('#', 1)
                hasInlineComment = True if len(keyValueAndComment) == 2 else False
                if(hasInlineComment):
                    line = keyValueAndComment[0]
                keyValue = line.split('=', 1)
                if(len(keyValue) != 2):
                    raise ValueError(f"file contains bad line format [LineNo:{lineNo}]: key/value pair is not separated with '='")

                key = keyValue[0].strip()
                val = keyValue[1].strip()
                conf[key] = val
                if(hasInlineComment): #it had an inline comment
                    self._AddFileLineOrder([key, keyValueAndComment[1]], "key,comment")
                else:    #regular key value pair
                    self._AddFileLineOrder(key, "key")
        return conf

    def _ExportSettingsFile(self, settingsObject, outputPath):
        allKeys = set(settingsObject.keys())
        with open(outputPath, "w", newline='\n') as fp:
            for orderLine in self._fileLineOrdering:
                order, data, type = orderLine
                if(type is None):
                    fp.write("\n")
                elif(type == "comment"):
                    fp.write(data + "\n")
                elif(type == "key") and (data in allKeys): #write out previously existing key
                    fp.write(f"{data}={settingsObject[data]}\n")
                    allKeys.remove(data)
                elif(type == "key,comment") and (data[0] in allKeys):
                    key, comment = data[0], data[1] 
                    fp.write(f"{key}={settingsObject[key]} #{comment}\n")
                    allKeys.remove(key)
            for newKey in allKeys:
                fp.write(f"{newKey}={settingsObject[newKey]}\n")
        return
