from CveXplore.main import CveXplore

try:
    from version import _version

    _version()
except ModuleNotFoundError:
    pass
