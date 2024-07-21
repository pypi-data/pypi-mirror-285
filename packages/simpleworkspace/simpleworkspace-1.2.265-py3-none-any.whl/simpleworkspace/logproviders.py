import logging as _logging
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import sys as _sys
import os as _os
import time as _time

class _BaseLogger:
    class Formatter(_logging.Formatter):
        def __init__(self, forceUTC=False, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if(forceUTC):
                self._timezoneStr = '+0000'
                self.converter = _time.gmtime
            else:
                self._timezoneStr = _time.strftime('%z') #uses '+HHMM'

        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                # support %z and %f in datefmt (struct_time doesn't carry ms or tz)
                datefmt = datefmt.replace("%f", "%03d" % int(record.msecs))
                datefmt = datefmt.replace('%z', self._timezoneStr)
                s = _time.strftime(datefmt, ct)
            else:
                s = _time.strftime(self.default_time_format, ct)
                if self.default_msec_format:
                    s = self.default_msec_format % (s, record.msecs)
            return s
        
        @classmethod
        def Factory(cls, useUTCTime=True, includeTime=True, includeLevel=True, includeTrace=True, includeProcessID=True, includeThreadID=False):
            '''Styling: "{Time} {Level} [PID={ProcessID},TID={ThreadID},TRC={moduleName}:{lineNo}]: <Message>"'''

            fmt = []
            if(includeTime):
                fmt.append('%(asctime)s')
            if(includeLevel):
                fmt.append('%(levelname)s')
            
            subFmt = []
            if(includeProcessID):
                subFmt.append('PID=%(process)d')
            if(includeThreadID):
                subFmt.append('TID=%(thread)d')
            if(includeTrace):
                subFmt.append('TRC=%(module)s:%(lineno)s')
            if(len(subFmt) > 0):
                subfmt = ','.join(subFmt)
                fmt.append(f'[{subfmt}]')
            
            fmt = ' '.join(fmt) 
            if(fmt):
                fmt += ": "
            fmt += "%(message)s"

            return cls(forceUTC=useUTCTime, fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S.%f%z")

    
    @staticmethod
    def RegisterAsUnhandledExceptionHandler(logger):
        def UncaughtExeceptionHandler(exc_type, exc_value, exc_traceback):
            if not issubclass(exc_type, KeyboardInterrupt): #avoid registering console aborts such as ctrl+c etc
                logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            _logging.shutdown()
            _sys.__excepthook__(exc_type, exc_value, exc_traceback)

        _sys.excepthook = UncaughtExeceptionHandler
    
class RotatingFileLogger:
    @classmethod
    def GetLogger(cls, 
                  filepath, minimumLogLevel=_logging.DEBUG, 
                  maxBytes=_ByteEnum.MegaByte.value * 30, maxRotations=10, 
                  useUTCTime=True, registerGlobalUnhandledExceptions=False,
                  fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=True, 
                  fmt_includeProcessID=True, fmt_includeThreadID=False):
        
        logger = _logging.getLogger(f"__ROTATINGFILELOGGER_{hash((filepath,minimumLogLevel,maxBytes,maxRotations,useUTCTime,fmt_includeTime,fmt_includeLevel,fmt_includeTrace,fmt_includeProcessID,fmt_includeThreadID))}")
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        FileLogger._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        logger.addHandler(cls.CreateHandler(
            filepath=filepath, useUTCTime=useUTCTime,
            maxBytes=maxBytes, maxRotations=maxRotations,
            fmt_includeTime=fmt_includeTime, fmt_includeLevel=fmt_includeLevel, fmt_includeTrace=fmt_includeTrace,
            fmt_includeProcessID=fmt_includeProcessID, fmt_includeThreadID=fmt_includeThreadID))
    

        return logger

    @classmethod
    def CreateHandler(cls, 
            filepath:str, useUTCTime=True,
            maxBytes=_ByteEnum.MegaByte.value * 100, maxRotations=10, 
            fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=True, 
            fmt_includeProcessID=True, fmt_includeThreadID=False):
            
            def rotator(source, dest):
                import gzip 
                with open(source, "rb") as sf:
                    gzip_fp = gzip.open(dest, "wb")
                    gzip_fp.writelines(sf)
                    gzip_fp.close()
                _os.remove(source)

            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=maxRotations, encoding='utf-8')
            handler.rotator = rotator
            handler.namer = lambda name: name + ".gz"
            handler.setFormatter(_BaseLogger.Formatter.Factory(
                useUTCTime=useUTCTime, includeTime=fmt_includeTime, includeLevel=fmt_includeLevel, 
                includeTrace=fmt_includeTrace, includeProcessID=fmt_includeProcessID, 
                includeThreadID=fmt_includeThreadID))
            return handler

class FileLogger:
    @classmethod
    def GetLogger(cls, 
                  filepath, minimumLogLevel=_logging.DEBUG, 
                  useUTCTime=True, registerGlobalUnhandledExceptions=False,
                  fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=True, 
                  fmt_includeProcessID=True, fmt_includeThreadID=False):
        logger = _logging.getLogger(f"__FILELOGGER_{hash((filepath,minimumLogLevel,useUTCTime,fmt_includeTime,fmt_includeLevel,fmt_includeTrace,fmt_includeProcessID,fmt_includeThreadID))}")
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        cls._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        logger.addHandler(cls.CreateHandler(
            filepath=filepath, useUTCTime=useUTCTime, 
            fmt_includeTime=fmt_includeTime, fmt_includeLevel=fmt_includeLevel, fmt_includeTrace=fmt_includeTrace,
            fmt_includeProcessID=fmt_includeProcessID, fmt_includeThreadID=fmt_includeThreadID))
        return logger
    
    @classmethod
    def CreateHandler(cls, filepath:str, useUTCTime=False, fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=False, fmt_includeProcessID=False, fmt_includeThreadID=False):
        handler = _logging.FileHandler(filepath, encoding='utf-8')
        handler.setFormatter(_BaseLogger.Formatter.Factory(
            useUTCTime=useUTCTime, includeTime=fmt_includeTime, includeLevel=fmt_includeLevel, 
            includeTrace=fmt_includeTrace, includeProcessID=fmt_includeProcessID, 
            includeThreadID=fmt_includeThreadID))
        return handler
    
    @staticmethod
    def _CreateParentFolders(filepath:str):
        filepath = _os.path.realpath(filepath)
        directoryPath = _os.path.dirname(filepath)
        if(directoryPath in ("", "/")):
            return
        _os.makedirs(directoryPath, exist_ok=True)

class StreamLogger:
    @classmethod
    def GetLogger(cls, 
                  minimumLogLevel=_logging.DEBUG, useUTCTime=False, 
                  registerGlobalUnhandledExceptions=False,  stream=_sys.stdout,
                  fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=False, 
                  fmt_includeProcessID=False, fmt_includeThreadID=False):
        stdoutLogger = _logging.getLogger(f"__STDOUTLOGGER__{hash((minimumLogLevel,useUTCTime,fmt_includeTime,fmt_includeLevel,fmt_includeTrace,fmt_includeProcessID,fmt_includeThreadID,stream))}")
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(stdoutLogger)
        if(stdoutLogger.hasHandlers()):
            return stdoutLogger
        stdoutLogger.setLevel(minimumLogLevel)
        stdoutLogger.addHandler(cls.CreateHandler(
            stream=stream, useUTCTime=useUTCTime, 
            fmt_includeTime=fmt_includeTime, fmt_includeLevel=fmt_includeLevel, fmt_includeTrace=fmt_includeTrace,
            fmt_includeProcessID=fmt_includeProcessID, fmt_includeThreadID=fmt_includeThreadID))
        return stdoutLogger
    
    @staticmethod
    def CreateHandler(stream=_sys.stdout, useUTCTime=False, fmt_includeTime=True, fmt_includeLevel=True, fmt_includeTrace=False, fmt_includeProcessID=False, fmt_includeThreadID=False):
        """
        A handler that can be supplied into a logger
        >>> logger.addHandler(StreamLogger.CreateHandler())
        """
        handler = _logging.StreamHandler(stream)
        handler.setFormatter(_BaseLogger.Formatter.Factory(useUTCTime=useUTCTime, includeTime=fmt_includeTime, includeLevel=fmt_includeLevel, includeTrace=fmt_includeTrace, includeProcessID=fmt_includeProcessID, includeThreadID=fmt_includeThreadID))
        return handler

class DummyLogger:
    @classmethod
    def GetLogger(cls):
        dummyLogger = _logging.getLogger("@@BLACKHOLE@@")
        if(dummyLogger.hasHandlers()):
            return dummyLogger
        dummyLogger.addHandler(_logging.NullHandler())
        dummyLogger.propagate = False
        return dummyLogger
