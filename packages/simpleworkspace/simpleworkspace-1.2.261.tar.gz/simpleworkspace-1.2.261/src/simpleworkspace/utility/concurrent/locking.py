import os as _os, sys as _sys
from typing import cast as _cast
import errno as _errno
from contextlib import suppress as _suppress
from simpleworkspace.types.time import TimeSpan as _TimeSpan

__ISWIN__ = _sys.platform.startswith("win")


class FileLock():
    """
    Manages system-wide exclusive file locks for given lock keys.

    A FileLock ensures that certain operations are performed synchronously across system boundaries by creating a file and 
    applying a system-wide lock to it. This lock remains active until it is explicitly released or the program exits, 
    preventing other programs from acquiring the same lock.

    This implementation supports managing multiple locks concurrently. By providing multiple lock keys, the FileLock class 
    will attempt to acquire the first available lock from the provided pool. For example, to restrict a process to run 
    only 4 instances simultaneously, you can provide 4 different lock keys.
    """

    class _LockContext:
        def __init__(self, key:str) -> None:
            import simpleworkspace.io.file, tempfile

            self.key = key
            self.filepath = _os.path.join(tempfile.gettempdir(), f"pyswl_{simpleworkspace.io.file.SanitizeFilename(key)}.lock")
            self._filehandle = None
            self._mode = 0o644

    def __init__(self, *keys: str) -> None:
        if not keys:
            raise ValueError('At least one lock key must be supplied')
        self._locks = [self._LockContext(x) for x in keys]
        self._acquiredLock: FileLock._LockContext|None = None
    
    @property
    def AcquiredLock(self):
        return self._acquiredLock

    def _windows_acquire(self, lockContext:_LockContext):
        """If the file lock could be acquired, lockContext will hold the file handle of the lock file."""

        import msvcrt

        self._raise_on_not_writable_file(lockContext.filepath)
        flags = (
            _os.O_RDWR  # open for read and write
            | _os.O_CREAT  # create file if not exists
            | _os.O_TRUNC  # truncate file if not empty
        )
        try:
            fh = _os.open(lockContext.filepath, flags, lockContext._mode)
        except OSError as exception:
            if exception.errno != _errno.EACCES:  # has no access to this lock
                raise
        else:
            try:
                msvcrt.locking(fh, msvcrt.LK_NBLCK, 1)
            except OSError as exception:
                _os.close(fh)  # close file first
                if exception.errno != _errno.EACCES:  # file is already locked
                    raise
            else:
                lockContext._filehandle = fh
                self._acquiredLock = lockContext

    def _windows_release(self, lockContext:_LockContext):
        """Releases the lock and sets clears filehandle and aquiredLock context"""
        import msvcrt

        fh = _cast(int, lockContext._filehandle)
        msvcrt.locking(fh, msvcrt.LK_UNLCK, 1)
        lockContext._filehandle = None
        self._acquiredLock = None
        _os.close(fh)

        with _suppress(OSError):  # Probably another instance of the application had acquired the file lock.
            _os.unlink(lockContext.filepath)

    def _unix_acquire(self, lockContext:_LockContext):
        """If the file lock could be acquired, lockContext will hold the file handle of the lock file."""

        import fcntl

        self._raise_on_not_writable_file(lockContext.filepath)

        flags = _os.O_RDWR | _os.O_TRUNC
        if not _os.path.exists(lockContext.filepath):
            flags |= _os.O_CREAT

        fh = _os.open(lockContext.filepath, flags, lockContext._mode)
        with _suppress(PermissionError):  # This locked is not owned by this UID
            _os.fchmod(fh, lockContext._mode)
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exception:
            _os.close(fh)
            if exception.errno == _errno.ENOSYS:  # NotImplemented error
                msg = "FileSystem does not appear to support flock"
                raise NotImplementedError(msg) from exception
        else:
            lockContext._filehandle = fh
            self._acquiredLock = lockContext

    def _unix_release(self, lockContext:_LockContext):
        """Releases the lock and sets clears filehandle and aquiredLock context"""
        import fcntl

        # Do not remove the lockfile:
        #   https://github.com/tox-dev/py-filelock/issues/31
        #   https://stackoverflow.com/questions/17708885/flock-removing-locked-file-without-race-condition
        fd = _cast(int, lockContext._filehandle)
        fcntl.flock(fd, fcntl.LOCK_UN)
        lockContext._filehandle = None
        self._acquiredLock = None
        _os.close(fd)

    def Acquire(self, blocking=False, timeout: _TimeSpan = None, poll_interval=_TimeSpan(milliSeconds=100)):
        """Tries to aquire a system wide file lock. 
        The lock lives until either release is called or no references left to instance

        :param blocking: when blocking is enabled, waits until a lock is available. \
            When blocking is not used, an exception is thrown if a lock can't be acquired immediately
        :param timeout: duration to wait before timing out when blocking is enabled
        :param poll_interval: How often to recheck acquire status
        :returns: self instance, to enable support for context manager

        :raises TimeoutError: When blocking is not used and lock is busy, or when blocking is enabled and timeout reached

        :Examples:
        
        Scope:
        >>> lock = FileLock("lockID")
        >>> lock.Acquire() #raises timeout when not acquirable
        >>> lock.Release()

        ContextManager:
        >>> with FileLock("lockID").Acquire():
        >>>     ...
        """

        import time
        from simpleworkspace.utility.time import StopWatch

        if self.AcquiredLock:
            return self

        stopwatch = StopWatch()
        stopwatch.Start()
        while True:
            for lock in self._locks:
                if(__ISWIN__):
                    self._windows_acquire(lock)
                else:
                    self._unix_acquire(lock)

                if self.AcquiredLock:
                    return self

            if blocking is False:
                raise TimeoutError(f'Failed to immediately acquire a lock')

            if (timeout is not None) and (stopwatch.GetElapsedSeconds() > timeout.TotalSeconds):
                raise TimeoutError(f'Timeout acquiring lock after {timeout.TotalSeconds} seconds')

            time.sleep(poll_interval.TotalSeconds)
        return self
    

    def Release(self):
        if not self.AcquiredLock:
            return
        
        if(__ISWIN__):
            self._windows_release(self.AcquiredLock)
        else:
            self._unix_release(self.AcquiredLock)

    def __enter__(self):
        if not self.AcquiredLock:
            raise SyntaxError("A lock must be Acquired first")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.Release()

    def __del__(self):
        """Called when the lock object is deleted"""
        self.Release()

    def _raise_on_not_writable_file(self, filename: str) -> None:
        """
        Raise an exception if attempting to open the file for writing would fail.

        This is done so files that will never be writable can be separated from files that are writable but currently
        locked.

        :param filename: file to check
        :raises OSError: as if the file was opened for writing.

        """
        import stat

        try:  # use stat to do exists + can write to check without race condition
            file_stat = _os.stat(filename)  # noqa: PTH116
        except OSError:
            return  # File does not exist or other errors, nothing to do

        if file_stat.st_mtime == 0:
            return  # if _os.stat returns but modification is zero that's an invalid _os.stat - ignore it

        if not (file_stat.st_mode & stat.S_IWUSR):
            raise PermissionError(_errno.EACCES, "Permission denied", filename)

        if stat.S_ISDIR(file_stat.st_mode):
            if __ISWIN__:
                # On Windows, this is PermissionError
                raise PermissionError(_errno.EACCES, "Permission denied", filename)
            else:
                # On linux / macOS, this is IsADirectoryError
                raise IsADirectoryError(_errno.EISDIR, "Is a directory", filename)
