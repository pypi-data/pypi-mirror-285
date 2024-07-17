from abc import ABC
from datetime import datetime
from simpleworkspace.types.time import TimeSpan
from datetime import datetime, timedelta
import types

class ITask(ABC):
    '''
    Tasks needs to implement this interface to be loaded into task scheduler

    Implementation:
        * To have scheduled tasks implement: On_Schedule() together with either task_interval OR NextSchedule()
        * To have startup tasks implement: On_Startup()

    properties and methods for Derived classes:
        * task_interval
        * task_ignore
        * task_description
        * On_StartUp()
        * On_Schedule()
        * NextSchedule()
    '''
    task_interval:TimeSpan = None
    '''Runs On_Schedule event per specified interval, example: TimeSpan(minute=2), would run the task once ever 2 minutes'''
    task_ignore = False
    '''Can ignore a task from being picked up'''
    task_description = None
    '''When task results are logged, appends more information about this task'''

    _cache_lastRunDate: datetime = None
    _task_id: str
    '''An unique identifier for this task, is used to store persistant task states and for lookups'''

    def On_StartUp(self) -> str|None:
        '''
        runs once per start of taskscheduler

        :return: When a string message is returned, it gets logged together with the task result
        '''

    def On_Schedule(self) -> str|None:
        '''
        runs once per specified interval or custom NextSchedule logic

        :return: When a string message is returned, it gets logged together with the task result
        '''

    def NextSchedule(self, previousRunDate: datetime|None) -> bool:
        '''
        Dictates if task ready for a scheduled run. By default relies upon task_interval being surpassed,
        if you need more custom scheduling control you may override this
        '''

        if(previousRunDate is None):
            return True
        nextRunDate = previousRunDate + timedelta(seconds=self.task_interval.TotalSeconds)
        if(datetime.now() > nextRunDate):
            return True
        return False
    
    @property 
    def _HasEvent_Schedule(self):
        if(self.task_interval is None) and not (self._HasImplementedFunc(self.NextSchedule)): # no scheduler used, therefore would never be triggered
            return False
        if not (self._HasImplementedFunc(self.On_Schedule)): #schedule function is not implemented, therefore no actions to perform
            return False
        return True

    @property
    def _HasEvent_StartUp(self):
        if not(self._HasImplementedFunc(self.On_StartUp)): #startup function is not implemented
            return False
        return True

    def _HasImplementedFunc(self, func: types.FunctionType|types.MethodType):
        #a methodtype is a class method, a functiontype on other hand is lamdba or local function etc

        if(isinstance(func, types.MethodType)) and ( func.__func__ is getattr(ITask, func.__name__)): #still original method
            return False
        return True
    
    def __new__(cls, *args, **kwargs):
        '''Gives possibility to ensure logic always run even if __init__ is left out. __init__ runs after this method has ran to completion'''
        instance = super().__new__(cls)
        instance._task_id = cls.__module__ + "." + cls.__name__
        return instance
    

class CommandTask(ITask):
    '''Premade task for running a simple command'''
    def __init__(self, command:str|list[str], onInterval:TimeSpan=None, onStartup=False) -> None:
        from hashlib import md5
        import shlex

        super().__init__()

        if(onInterval is None) and not (onStartup):
            raise ValueError("No schedules specified for command, use interval or startup")
        
        if(onInterval is not None):
            if type(onInterval) is not TimeSpan:
                raise TypeError(f"interval must be of type {type(TimeSpan)}")
            self.task_interval = onInterval
        if onStartup:
            def On_StartUp():
                return self.On_Schedule()
            self.On_StartUp = On_StartUp
            
        if isinstance(command, str):
            command = shlex.split(command)
        self.command = command
        commandStringRepresentation = ' '.join(command)
        self.task_description = commandStringRepresentation

        #adjust taskid since normal retrieved task id would not be unique per command
        self._task_id = md5(commandStringRepresentation.encode()).hexdigest()[:16]

    def On_Schedule(self):
        import subprocess
        
        creationflags = 0
        if(hasattr(subprocess, 'CREATE_NO_WINDOW')): #on windows os avoid showing console when running in .pyw mode
            creationflags = subprocess.CREATE_NO_WINDOW
        result = subprocess.run(self.command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
        message = ""
        if(result.returncode != 0): #something went bad
            stderr = ""
            if(result.stderr is not None):
                stderr = result.stderr.rstrip()
            message += f"STDERR[{result.returncode}]: {stderr};"
        
        if(result.stdout):
            message += f"STDOUT: {result.stdout.rstrip()};"

        return message
