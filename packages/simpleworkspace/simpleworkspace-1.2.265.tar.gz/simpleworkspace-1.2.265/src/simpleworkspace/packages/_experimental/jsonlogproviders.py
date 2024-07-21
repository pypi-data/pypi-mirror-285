import logging as _logging
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import sys as _sys
import os as _os
import time as _time
import json

class _BaseLogger:
    class JSONFormatter(_logging.Formatter):
        def __init__(self, forceUTC=False, indent:bool=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.indent = indent
            if (_time.timezone == 0) or (forceUTC):
                self._timezoneStr = 'Z'
                self.converter = _time.gmtime #needed when forcing utc on a non utc system
            else:
                self._timezoneStr = _time.strftime('%z') #uses '+HHMM'

        def _json_serializable(obj):
            try:
                return obj.__dict__
            except AttributeError:
                return str(obj)
    
        def formatTime(self, record, datefmt="%Y-%m-%dT%H:%M:%S.%f%z"):
            #normally this supports changing datefmt, but we hardcode the iso8601 instead

            ct = self.converter(record.created)
            datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
            datefmt = datefmt.replace('%z', self._timezoneStr)
            s = _time.strftime(datefmt, ct)
            return s
        
        def format(self, record: _logging.LogRecord) -> str:
            msg = {
                'Time': self.formatTime(record),
                'Level': record.levelname,
                'Message': record.getMessage(),
                'Module': record.module,
                'LineNo': record.lineno,
                'ThreadNo': record.thread,
                'ProcessNo': record.process,
            }

            if hasattr(record, 'extra'):
                msg['Extra'] = record.extra

            if record.exc_info:
                # Cache the traceback text to avoid converting it multiple times
                # (it's constant anyway)
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            if record.exc_text:
                msg['Exception'] = self.formatException(record.exc_info)
                if record.stack_info:
                    msg["Exception"] += '\n' + self.formatStack(record.stack_info)


            try:
                return json.dumps(
                    msg,
                    default=self._json_serializable,
                    indent='\t' if self.indent else None,
                )    
            # "ValueError: Circular reference detected" is raised when there is a reference to object inside the object itself.
            except (TypeError, ValueError, OverflowError) as ex:
                return f'{{"_write_error":"{ex}"}}'
                
    
    @staticmethod
    def RegisterAsUnhandledExceptionHandler(logger):
        def UncaughtExeceptionHandler(exc_type, exc_value, exc_traceback):
            if not issubclass(exc_type, KeyboardInterrupt): #avoid registering console aborts such as ctrl+c etc
                logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            _logging.shutdown()
            _sys.__excepthook__(exc_type, exc_value, exc_traceback)

        _sys.excepthook = UncaughtExeceptionHandler
    

class FileLogger:
    @classmethod
    def GetLogger(cls, 
                  filepath, minimumLogLevel=_logging.DEBUG, 
                  useUTCTime=True, registerGlobalUnhandledExceptions=False):
        logger = _logging.getLogger(f"__FILELOGGER_{hash((filepath,minimumLogLevel,useUTCTime))}")
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        cls._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        logger.addHandler(cls.CreateHandler(filepath=filepath, useUTCTime=useUTCTime))
        return logger
    
    @classmethod
    def CreateHandler(cls, filepath:str, useUTCTime=False):
        handler = _logging.FileHandler(filepath, encoding='utf-8')
        handler.setFormatter(_BaseLogger.JSONFormatter(forceUTC=useUTCTime))
        return handler
    
    @staticmethod
    def _CreateParentFolders(filepath:str):
        filepath = _os.path.realpath(filepath)
        directoryPath = _os.path.dirname(filepath)
        if(directoryPath in ("", "/")):
            return
        _os.makedirs(directoryPath, exist_ok=True)
