import os as _os
from simpleworkspace.types.os import OperatingSystemEnum as _OperatingSystemEnum
import subprocess as _subprocess

class CommandBuilder:            
    def __init__(self):
        self._os = _OperatingSystemEnum.GetCurrentOS()
        self._eolSequence = "\r\n" if self._os == _OperatingSystemEnum.Windows else "\n"
        self._commentSequence = "@REM" if self._os == _OperatingSystemEnum.Windows else "#"
        self._shellType = "cmd.exe" if self._os == _OperatingSystemEnum.Windows else "/bin/sh"
        self._queuedCommands:list[str] = []

        self._QueueDefaults()

    def _QueueDefaults(self):
        if(self._os == _OperatingSystemEnum.Windows):
            self.Queue('@echo off')
        else:
            self.Queue('#!/bin/sh')
    
    def Clear(self):
        self.__init__()

    def Queue(self, command:str, isComment = False, escapeNewlines=False):
        """Queues a shell command

        :param isComment: when true, comments out the command
        :param escapeNewlines: escapes newlines by replacing them with a space ' '
        """
        if(escapeNewlines):
            command = command.replace('\r\n', ' ')
            command = command.replace('\n', ' ')
        if(isComment):
            command = f'{self._commentSequence} {command}'
            command = command.replace('\n', f'\n{self._commentSequence} ') #if there are newlines, comment those out aswell
        self._queuedCommands.append(command)

    def Execute(self, stream_stdout=_subprocess.PIPE, stream_stderr=_subprocess.PIPE):
        import tempfile

        try:
            # Create a temporary file
            fileExtension = 'bat' if self._os == _OperatingSystemEnum.Windows else "sh"
            fp = tempfile.NamedTemporaryFile(prefix='__CommandBuilder__', suffix=f'.{fileExtension}', delete=False)
            for line in self.Reader():
                fp.write(line.encode())
            fp.close()
                
            runCommand = [self._shellType, fp.name]
            if(self._os == _OperatingSystemEnum.Windows):
                runCommand = [self._shellType, "/c", fp.name] #when invoking with cmd.exe, it requires the /c flag
            result = _subprocess.run(
                runCommand,
                stdout=stream_stdout, 
                stderr=stream_stderr 
            )

            if(result.returncode != 0): #something went bad
                raise ChildProcessError(f'Script execution got bad return code({result.returncode}), STDERR: {result.stderr}')
            return result
        finally:
            fp.close()
            _os.remove(fp.name)


    def Reader(self):
        ''' Iterator to read the generatable file line by line '''
        for line in self._queuedCommands:
            yield line + self._eolSequence + self._eolSequence

    def __str__(self):
        return ''.join(self.Reader())