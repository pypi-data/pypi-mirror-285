from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import play as _play

play: '_play' = __LazyImporter__(__package__, '.play')
