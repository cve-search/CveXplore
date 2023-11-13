"""
epss
====
"""
from CveXplore.common.data_source_connection import DatasourceConnection


class Epss(DatasourceConnection):
    """
    Epss database object
    """

    def __init__(self, **kwargs):
        super().__init__("epss")

        for each in kwargs:
            setattr(self, each, kwargs[each])

    def __repr__(self):
        """String representation of object"""
        return "<< Epss:{} >>".format(self.epss)
