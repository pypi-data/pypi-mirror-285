import hashlib as _hashlib
import string as _string
from typing import Iterator as _Iterator, TypeVar as _TypeVar, Type as _Type
import os as _os

_T = _TypeVar('_T')

def Read(filepath: str, readLimit:int=None, readOffset=0, type:_Type[_T]|_Type=str) -> _T:
    """
    :readLimit: Max amount of bytes to read
    :type: specifies return type of str or bytes
    :returns: the file data as str or bytes
    """

    if(type not in (str,bytes)):
        raise TypeError("return type can only be bytes or str")
    if(readLimit is None):
        readLimit = -1 # -1 is the None equivalent for filehandles

    openMode = "rb" if type is bytes else "r"
    with open(filepath, openMode, newline=None) as fp:
        fp.seek(readOffset)
        return fp.read(readLimit)
    
def ReadIterator(filepath: str, readSize:int, readLimit:int=None, readOffset=0, type:_Type[_T]|_Type=str) -> _Iterator[_T]:
    """
    reads file in chunks without loading all at once into memory

    :readSize: amount of bytes to read each iteration
    :readLimit: Max amount of bytes to read
    :type: specifies return type of str or bytes
    :returns: iterator with str or byte chunk
    """

    if(readSize < 1):
        raise ValueError('readSize cannot be less than 1 byte')
    if(type not in (str,bytes)):
        raise TypeError("return type can only be bytes or str")
    if(readLimit is None):
        readLimit = -1 # -1 is the None equivalent for filehandles

    if (readLimit < readSize and readLimit >= 0):
        readSize = readLimit

    openMode = "rb" if type is bytes else "r"
    totalRead = 0
    with open(filepath, openMode, newline=None) as fp:
        fp.seek(readOffset)
        while True:
            if readLimit != -1 and totalRead >= readLimit:
                break
            data = fp.read(readSize)
            totalRead += readSize
            
            if not data:
                break

            yield data
    return

def Hash(filePath: str, hashFn=_hashlib.sha1) -> str:
    from simpleworkspace.types.byte import ByteEnum
    hashObj:_hashlib._Hash = hashFn()
    for data in ReadIterator(filePath, readSize=ByteEnum.KiloByte.value * 500, type=bytes):
        hashObj.update(data)
    return hashObj.hexdigest()
    
def Create(filepath: str, data: bytes | str = None):
    '''Creates or overwrites file if exists'''

    if type(data) is str:
        data = data.encode()
    with open(filepath, "wb") as file:
        if data is not None:
            file.write(data)

def Append(filepath: str, data: bytes | str):
    if type(data) is bytes:
        pass  # all good
    elif type(data) is str:
        data = data.encode()
    else:
        raise Exception("Only bytes or string can be used to append to file")
    with open(filepath, "ab") as file:
        file.write(data)

def SecureDelete(filepath: str, passes:int = 1):
    """
    Securely delete a file by overwriting its contents with random data.

    :param filepath: Path to the file to be deleted securely.
    :param passes: Number of passes for overwriting the file.
    """
    
    if(passes < 1):
        raise ValueError("Less than 1 pass specified making a secure deletion not possible")

    CHUNKSIZE = 1000 * 500 #500kb
    with open(filepath, "r+b", buffering=0) as fp:
        fp.seek(0, _os.SEEK_END)
        FILESIZE = fp.tell()
        for _ in range(passes):
            fp.seek(0)
            totalWritten = 0
            while(totalWritten < FILESIZE):
                bytesToWrite = CHUNKSIZE
                if(FILESIZE - totalWritten < CHUNKSIZE):
                    bytesToWrite = FILESIZE - totalWritten
                fp.write(_os.urandom(bytesToWrite))
                totalWritten += bytesToWrite

    basePath = _os.path.dirname(filepath)
    newPath = _os.path.join(basePath, _os.urandom(6).hex())
    _os.rename(filepath, newPath)
    _os.remove(newPath)


def SanitizeFilename(filename:str, allowedCharset = _string.ascii_letters + _string.digits + " .-_"):
    from simpleworkspace.utility import strings
    return strings.Sanitize(filename, allowedCharset=allowedCharset)