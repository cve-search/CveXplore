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

    def to_dict(self):
        """
        Method to convert the entire object to a dictionary

        :return: Data from object
        :rtype: dict
        """

        return {k: v for (k, v) in self.__dict__.items() if not k.startswith("_")}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def __repr__(self):
        """ String representation of object """
        return "<< Via4:{} >>".format(self.id)
