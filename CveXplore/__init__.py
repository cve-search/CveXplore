try:
    from CveXplore.main import CveXplore
    from version import _version

    _version()
except ModuleNotFoundError:
    pass
