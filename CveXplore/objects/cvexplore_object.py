"""
CveXploreObject
===============
"""
from CveXplore.common.config import Configuration


class CveXploreObject(object):
    """
    CveXploreObject is the base object for all database collection objects
    """

    def __init__(self):
        self.config = Configuration

    def __repr__(self) -> str:
        return f"<< {self.__class__.__name__} >>"
