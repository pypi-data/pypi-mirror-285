from ...exceptions import VersionError

try:
    # Bliss <=1.11
    # This needs to be tried before Bliss >=2
    from .ndarrayv0 import PersistentNdArray
except VersionError:
    try:
        # Bliss >=2
        from .ndarrayv1 import PersistentNdArray
    except VersionError as exc:
        _EXC = exc

        def _reraise(*_, **kw):
            raise _EXC

        class BlissDataVersionNotSupported:
            def __getattr__(self, *_):
                return _reraise

        PersistentNdArray = BlissDataVersionNotSupported
