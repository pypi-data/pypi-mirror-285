from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import locking as _locking
    from . import parallel as _parallel

locking: '_locking' = __LazyImporter__(__package__, '.locking')
parallel: '_parallel' = __LazyImporter__(__package__, '.parallel')