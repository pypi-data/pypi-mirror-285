class App:
    @classmethod
    def Setup(cls, name: str, company: str = None, id: str = None, version="1.0.0"):
        """
        :param name: app name
        :param company: app company name
        :param id: \
            supply an id(such as a random guid) to be able to uniquely identify this app, \
            if not supplied appname+appcompany will be used as id
        """

        import os
        import simpleworkspace.io.directory
        import simpleworkspace.io.path
        from simpleworkspace.io.path import PathResolver
        from simpleworkspace.logproviders import RotatingFileLogger
        from simpleworkspace.settingsproviders import SettingsManager_JSON
        from hashlib import md5

        if (name is None) or (name == ""):
            raise ValueError("app name cannot be left empty")

        cls.name = name
        cls.company = company

        if id is None:
            id = name
            if company is not None:
                id += cls.company

        cls.id = md5(id.encode()).hexdigest()[:16]
        cls.version = version

        #roaming for windows since app settings may want to be shared/backuped across machines
        cls.path_AppData = PathResolver.User.AppData(name, company, roaming=True) 
        """windows example: C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName"""
        cls.path_AppData_Storage = os.path.join(cls.path_AppData, "storage")
        """windows example: 'C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName\\storage"""
        simpleworkspace.io.directory.Create(cls.path_AppData_Storage)  # creates parent folders aswell

        cls.logger = RotatingFileLogger.GetLogger(os.path.join(cls.path_AppData, "app.log"), registerGlobalUnhandledExceptions=True)
        cls.settingsManager = SettingsManager_JSON(os.path.join(cls.path_AppData, "config.json"))
        cls.settingsManager.LoadSettings()

    @classmethod
    def PreventMultipleInstances(cls):
        cls.__EnsureInitialized()

        from simpleworkspace.utility.concurrent.locking import FileLock

        cls.__globalAppLock__ = FileLock(cls.id)
        try:
            cls.__globalAppLock__.Acquire()
        except TimeoutError as ex:
            exit("Another instance is already running... exiting()")

    @classmethod
    def __EnsureInitialized(cls):
        if not hasattr(cls, "id"):
            raise ValueError("Incorrect Usage, Call App.Setup() first.")
