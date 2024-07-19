from typing import Callable as _Callable, Iterator as _Iterator
import os as _os

def Create(path: str):
    '''Create all non existing directiores in specified path, ignores if exists.'''
    _os.makedirs(path, exist_ok=True)

def RemoveTree(path: str) -> None:
    '''Use with caution! Removes removes a complete directory tree'''
    from simpleworkspace.utility import strings
    import shutil
    if(strings.IsNullOrEmpty(path)) or (path == '/') or (path == '\\'):
        raise ValueError(f'Tree removal of "{path}" might be unsafe and was cancelled as precaution')
    shutil.rmtree(path, ignore_errors=True)


def Scan(
        searchDirectory: str,
        yieldDirs=True, yieldFiles=True, followLinks=False,
        filter:str|list[str]|_Callable[[str],bool]=None,
        maxDepth: int=None
        ) -> _Iterator[str]:
    """
    Recursively iterate all directories in a path.
    All yielded paths are normalized with forwardslashes. 
    Yielded paths are relative to searchDirectory and therefore not necessarily absolute paths.
    All encountered exceptions are ignored

    :param yieldDirs: When true yields directories. Keep in mind even if this is set to false it will scan the directory tree but simply not yield its path
    :param yieldFiles: When true yields files.
    :param followLinks: Specifies wheter to yield symlinks, when this is set to false, symlink directories wont even be scanned.
    :param filter: Callback or Glob string(s), filters recieves the normalized path, when the filter condition is true, the path is yielded.
        * Callback            : receieves path as argument and returns true for paths that should be yielded
        * Glob String or List : Test glob pattern against current path, paths are yielded on match. Examples: "*.js" or ["*.js", "*.txt"] \n
    :param maxDepth: Specify how many levels down to list folders, level/depth 1 is basically searchDir entries
    :returns: an iterator of full matching paths
    """
    from simpleworkspace.utility import regex

    searchDirectory = searchDirectory.replace('\\', '/') #replacing backslashes on entry dir since os.join wont do it later
    
    if isinstance(filter, str):
        filter = filter.replace('\\', '/')
        filter = lambda path, filter=filter: regex.Glob(filter, path)
    elif isinstance(filter, (list, tuple)):
        filter = [pattern.replace('\\', '/') for pattern in filter]
        filter = lambda path, filter=filter: any(regex.Glob(pattern, path) for pattern in filter)
    

    def Recurse(path:str, currentDepth:int):
        try:
            with _os.scandir(path) as entries:
                for entry in entries:
                    if(not followLinks) and (entry.is_symlink()):
                        continue

                    entryPath = entry.path
                    if(_os.path.sep != '/'): #since os does not use forward slash, os.join() have appended with backslash
                        entryPath = entryPath.replace(_os.path.sep, '/')

                    if filter is None:
                        pathMatchesFilter = True
                    else: #callback
                        pathMatchesFilter = filter(entryPath)
                    
                    if entry.is_file():
                        if (yieldFiles and pathMatchesFilter):
                            yield entryPath
                    elif(entry.is_dir()):
                        if (yieldDirs and pathMatchesFilter):
                            yield entryPath
                        nextDepth = currentDepth + 1
                        if (maxDepth is not None) and (nextDepth > maxDepth):
                            continue
                        yield from Recurse(entryPath, currentDepth=nextDepth)
                    else:
                        pass #skip other type of entries
        except (PermissionError, FileNotFoundError, NotADirectoryError) as ex: 
            #common raises that can safely be skipped!

            #PermissionError: not enough permission to browse folder, a common error when recursing unkown dirs, simply skip if no exception callback

            #FileNotFound or NotADirectory errors:
            #   since we know we had a valid path from beginning, this is most likely that a file or folder
            #   was removed/modified by another program during our search
            pass
        except (OSError, InterruptedError, UnicodeError):
            #this one is tricker and might potentially be more important, eg a file can temporarily not be accessed being busy etc.
            #this is still a common exception when recursing very deep, so we don't act on it

            #InterruptedError: Raised if the os.scandir() call is interrupted by a signal.
            #UnicodeError: Raised if there are any errors while decoding the file names returned by os.scandir().
            pass
        except Exception as e:
            #here something totally unexpected has happened such as a bad callback supplied by user etc,
            #this one always raises exception

            #an completely invalid input supplied to os.scandir() such as empty string or a string not representing a directory
            #might raise TypeError and ValueError, we dont specifically handle these since we in these cases want to fully
            #raise an exception anyway

            raise e
            

    
    if not _os.path.isdir(searchDirectory):
        raise NotADirectoryError(f'Supplied path is not a valid directory: "{searchDirectory}"')

    yield from Recurse(searchDirectory, 1)
