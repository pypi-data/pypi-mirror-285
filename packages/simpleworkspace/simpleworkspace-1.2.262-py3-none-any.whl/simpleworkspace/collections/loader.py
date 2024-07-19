from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import observables as _observables
observables: '_observables' = __LazyImporter__(__package__, '.observables')