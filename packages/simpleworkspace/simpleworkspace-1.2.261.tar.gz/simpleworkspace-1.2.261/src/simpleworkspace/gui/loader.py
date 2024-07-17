from simpleworkspace.__lazyimporter__ import __LazyImporter__, __TYPE_CHECKING__
if(__TYPE_CHECKING__):
    from . import dialogs as _dialogs

dialogs: '_dialogs' = __LazyImporter__(__package__, '.dialogs')
