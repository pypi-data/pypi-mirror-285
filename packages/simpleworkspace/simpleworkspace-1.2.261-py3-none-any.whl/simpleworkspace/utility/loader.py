from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import module as _module
    from . import regex as _regex
    from . import time as _time
    from . import strings as _strings
    from . import bytes as _bytes
    from . import linq as _linq
    from . import progressbar as _progressbar
    from . import encryption as _encryption
    from .concurrent import loader as _concurrent
    from .cli import loader as _cli

module: '_module' = __LazyImporter__(__package__, '.module')
regex: '_regex' = __LazyImporter__(__package__, '.regex')
time: '_time' = __LazyImporter__(__package__, '.time')
strings: '_strings' = __LazyImporter__(__package__, '.strings')
bytes: '_bytes' = __LazyImporter__(__package__, '.bytes')
linq: '_linq' = __LazyImporter__(__package__, '.linq')
progressbar: '_progressbar' = __LazyImporter__(__package__, '.progressbar')
encryption: '_encryption' = __LazyImporter__(__package__, '.encryption')
concurrent: '_concurrent' = __LazyImporter__(__package__, '.concurrent.loader')
cli: '_cli' = __LazyImporter__(__package__, '.cli.loader')
