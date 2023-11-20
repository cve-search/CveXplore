"""
via4
====
"""
from CveXplore.common.data_source_connection import DatasourceConnection


class Via4(DatasourceConnection):
    """
    Via4 database object
    """

    def __init__(self, **kwargs):
        super().__init__("via4")

        for each in kwargs:
            setattr(self, each, kwargs[each])

    def __repr__(self):
        """String representation of object"""
        return f"<< Via4:{self.id} >>"
