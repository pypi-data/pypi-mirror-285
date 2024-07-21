import os as _os
from typing import Callable as _Callable, BinaryIO as _BinaryIO



class GZIP:
    @staticmethod
    def Create(inputPath: str, outputPath: str = None):
        """Compresses one file to a GZIP archive

        :param inputPath: filepath to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :return: the path to the compressed archive
        """
        import gzip

        if outputPath is None:
            outputPath = inputPath + ".gz"
        with open(inputPath, mode="rb") as f_in:
            with gzip.open(outputPath, mode="wb") as f_out:
                f_out.writelines(f_in)
        return outputPath

    @staticmethod
    def Extract(inputPath: str, outputPath: str = None):
        """Extracts one file to a GZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import gzip

        if outputPath is None:
            outputPath = inputPath.removesuffix(".gz")
        with gzip.open(inputPath, mode="rb") as f_in:
            with open(outputPath, mode="wb") as f_out:
                f_out.writelines(f_in)
        return outputPath

    @classmethod
    def Scan(cls, inputPath:str):
        import gzip, io
        
        with gzip.open(inputPath, mode='rb') as archive:
            archive.seek(0, io.SEEK_END)
            entry = _ArchiveEntry(
                path = _os.path.basename(inputPath),
                size=archive.tell(),
                isDirectory = False
            )
            entry._dataLoader = _ArchiveEntry._LazyIO(
                FileHandleFactory=lambda: gzip.open(inputPath, mode='rb')
            )
        return entry


class TAR:
    @staticmethod
    def Create(inputPath: str, outputPath: str = None, pipe_gz=True, ignoreErrors=False, filter:_Callable[[str], bool] = None):
        """Compresses file or folder to TAR or Tar+GZIP archive

        :param inputPath: file or folder path to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :param pipe_gz: If enabled, appends GZIP compression on top of the TAR archive which by itself is uncompressed.
        :param ignoreErrors: continue compressing next entry when encountering errors
        :param filter: recieves full filepath to each entry, returning true includes the file in the final archive
        :return: the path to the compressed archive
        """
        import tarfile

        archiveType = ".tar.gz" if pipe_gz else ".tar"
        mode = "w:gz" if pipe_gz else "w"

        if outputPath is None:
            outputPath = inputPath + archiveType

        with tarfile.open(outputPath, mode=mode) as archive:
            try:
                if _os.path.isfile(inputPath):
                    if(filter is None) or (filter(inputPath) == True):
                        archive.add(inputPath, arcname=_os.path.basename(inputPath))
                elif _os.path.isdir(inputPath):
                    for root, dirs, files in _os.walk(inputPath):
                        for dirName in dirs:
                            currentPath = _os.path.join(root, dirName)
                            if(filter is None) or (filter(currentPath) == True):
                                archive.add(currentPath, arcname=_os.path.relpath(currentPath, inputPath))
                        for file in files:
                            currentPath = _os.path.join(root, file)
                            if(filter is None) or (filter(currentPath) == True):
                                archive.add(currentPath, arcname=_os.path.relpath(currentPath, inputPath))
            except Exception as ex:
                if not ignoreErrors:
                    raise ex
        return outputPath

    @classmethod
    def Extract(cls, inputPath: str, outputPath: str = None):
        """Extracts TAR or TAR+GZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import tarfile

        def GetType(archivePath: str):
            validExt = (".tar", ".tar.gz", ".tgz")
            for ext in validExt:
                if archivePath.endswith(ext):
                    return ext
            raise NameError(f"File extension is not recognized, expected {validExt}")

        extension, mode = cls._GetArchiveType(inputPath)
        if outputPath is None:
            outputPath = inputPath.removesuffix(extension)

        with tarfile.open(inputPath, mode=mode) as tar:
            tar.extractall(outputPath)
        return outputPath

    @classmethod
    def Scan(cls, inputPath:str):
        import tarfile

        extension, mode = cls._GetArchiveType(inputPath)
        with tarfile.open(inputPath, mode=mode) as archive:
            for entry in archive:
                abstractEntry = _ArchiveEntry(
                    path = entry.name,
                    size = entry.size,
                    isDirectory = entry.isdir()
                )
                if(abstractEntry.IsFile):
                    abstractEntry._dataLoader = _ArchiveEntry._LazyIO(
                        FileHandleFactory=lambda: archive.extractfile(entry),
                    )
                yield abstractEntry

    @classmethod
    def _GetArchiveType(cls, archivePath: str):
        validExt = (".tar", ".tar.gz", ".tgz")
        for ext in validExt:
            if archivePath.endswith(ext):
                return ext,  "r" if ext == ".tar" else "r:gz"
        raise NameError(f"File extension is not recognized, expected {validExt}")
    

    



class ZIP:
    @staticmethod
    def Create(inputPath: str, outputPath: str = None, compressionLevel: int = None, ignoreErrors=False, filter:_Callable[[str], bool] = None):
        """Compresses file or folder to zip archive

        :param inputPath: file or folder path to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :param compressionLevel: 0-9, where 0 uses no compression(only stores files), and 9 has max compression. \
                                 When None is supplied use default in zlib(usually 6)
        :param ignoreErrors: continue compressing next entry when encountering errors
        :param filter: recieves full filepath to each entry, returning true includes the file in the final archive
        :return: the path to the compressed archive
        """
        import zipfile

        if outputPath is None:
            outputPath = inputPath + ".zip"
        compressionType = zipfile.ZIP_DEFLATED
        if (compressionLevel is not None) and (compressionLevel < 1):
            compressionType = zipfile.ZIP_STORED  # use no compression
            compressionLevel = None
        with zipfile.ZipFile(outputPath, mode="w", compression=compressionType, compresslevel=compressionLevel) as archive:
            try:
                if _os.path.isfile(inputPath):
                    if(filter is None) or (filter(inputPath) == True):
                        archive.write(inputPath, arcname=_os.path.basename(inputPath))
                elif _os.path.isdir(inputPath):
                    for root, dirs, files in _os.walk(inputPath):
                        for dirName in dirs:
                            currentPath = _os.path.join(root, dirName)
                            if(filter is None) or (filter(currentPath) == True):
                                archive.write(currentPath, arcname=_os.path.relpath(currentPath, inputPath))
                        for file in files:
                            currentPath = _os.path.join(root, file)
                            if(filter is None) or (filter(currentPath) == True):
                                archive.write(currentPath, arcname=_os.path.relpath(currentPath, inputPath))
            except Exception as ex:
                if not ignoreErrors:
                    raise ex
        return outputPath

    @staticmethod
    def Extract(inputPath: str, outputPath: str = None):
        """Extracts ZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import zipfile

        if outputPath is None:
            outputPath = inputPath.removesuffix(".zip")
        with zipfile.ZipFile(inputPath, mode="r") as zipf:
            zipf.extractall(outputPath)
        return outputPath
    
    @classmethod
    def Scan(cls, inputPath:str):
        import zipfile

        with zipfile.ZipFile(inputPath, mode="r") as archive:
            for entry in archive.filelist:
                abstractEntry = _ArchiveEntry(
                    path = entry.filename,
                    size = entry.file_size,
                    isDirectory = entry.is_dir(),
                )
                if(abstractEntry.IsFile):
                    abstractEntry._dataLoader = _ArchiveEntry._LazyIO(
                        FileHandleFactory=lambda: archive.open(entry),
                    )
                yield abstractEntry


class SevenZip:
    @staticmethod
    def Create(inputPath: str, outputPath: str = None, useCompression=True, password: str = None, ignoreErrors=False, filter:_Callable[[str], bool] = None):
        """Compresses file or folder to zip archive

        :param inputPath: file or folder path to compress
        :param outputPath: desired full output path, by default adds format suffix to inputpath
        :param useCompression: If false, use copy mode to store files without compression
        :param password: When password is supplied, encrypts the archive
        :param ignoreErrors: continue compressing next entry when encountering errors
        :param filter: recieves full filepath to each entry, returning true includes the file in the final archive
        :return: the path to the compressed archive
        """
        import py7zr  # pip install py7zr

        if outputPath is None:
            outputPath = inputPath + ".7z"

        filters = None if useCompression else [{"id": py7zr.FILTER_COPY}]
        if(filters is not None) and (password is not None):
            #special scenario / issue for this lib: 
            #   When a custom filter is specified, it completely overrides all default filters, we therefore have to
            #   manually specify for example that we want encryption filter when filters are overriden and a password is set  
            filters.append({"id": py7zr.FILTER_CRYPTO_AES256_SHA256})
    
        useHeaderEncryption = password is not None
        with py7zr.SevenZipFile(outputPath, mode="w", filters=filters, password=password, header_encryption=useHeaderEncryption) as archive:
            try:
                if _os.path.isfile(inputPath):
                    if(filter is None) or (filter(inputPath) == True):
                        archive.write(inputPath, arcname=_os.path.basename(inputPath))
                elif _os.path.isdir(inputPath):
                    for root, dirs, files in _os.walk(inputPath):
                        for dirName in dirs:
                            currentPath = _os.path.join(root, dirName)
                            if(filter is None) or (filter(currentPath) == True):
                                archive.write(currentPath, arcname=_os.path.relpath(currentPath, inputPath))
                        for file in files:
                            currentPath = _os.path.join(root, file)
                            if(filter is None) or (filter(currentPath) == True):
                                archive.write(currentPath, arcname=_os.path.relpath(currentPath, inputPath))
            except Exception as ex:
                if not ignoreErrors:
                    raise ex
        return outputPath

    @staticmethod
    def Extract(inputPath: str, outputPath: str = None, password: str = None):
        """Extracts ZIP archive

        :param inputPath: filepath to extract
        :param outputPath: desired full output path, by default removes format suffix from inputpath
        :return: the path to the extracted content
        """
        import py7zr  # pip install py7zr

        if outputPath is None:
            outputPath = inputPath.removesuffix(".7z")

        with py7zr.SevenZipFile(inputPath, mode="r", password=password) as archive:
            archive.extractall(outputPath)
        return outputPath

    @classmethod
    def Scan(cls, inputPath:str, password:str=None):
        '''Note: The py7zr library does not support true memory stream currently, when DataReader is used the entire file is loaded into memory'''
        import py7zr  # pip install py7zr

        with py7zr.SevenZipFile(inputPath, mode="r", password=password) as archive:
            for entry in archive.files:
                abstractEntry = _ArchiveEntry(
                    path=entry.filename,
                    id = str(entry.id),
                    size = entry.uncompressed,
                    isDirectory=entry.is_directory,
                )
                if(abstractEntry.IsFile):
                    abstractEntry._dataLoader = _ArchiveEntry._LazyIO(
                        FileHandleFactory=lambda: archive.read(entry.filename)[entry.filename],
                        onClosedEvent=lambda: archive.reset()
                    )
                yield abstractEntry


class _ArchiveEntry:
    def __init__(self, path: str, id:str=None, size:int=None, isDirectory=False) -> None:
        self.Path = path.rstrip('/\\')
        self.Id = self.Path if id is None else id
        self.Size = size
        self.IsDirectory = isDirectory
        self.IsFile = isDirectory == False


    def DataReader(self):
        '''
        Gets an io stream of archive data, is used with context manager
        >>> with entry.ReadData() as stream:...
        '''
        return self._dataLoader
    
    @property
    def Data(self):
        '''Loads the complete file data into memory'''
        with self.DataReader() as stream:
            return stream.read()
    
    _dataLoader:'_LazyIO'
    class _LazyIO:
        def __init__(self, FileHandleFactory:_Callable[[], _BinaryIO], onClosedEvent:_Callable = None):
            self._openFn = FileHandleFactory
            self._io:_BinaryIO
            self._onClosedEvent = onClosedEvent

        def __enter__(self):
            self._io = self._openFn()
            return self._io

        def __exit__(self, exc_type, exc_value, traceback):
            self._io.close()
            self._io = None
            if(self._onClosedEvent):
                self._onClosedEvent()