"""
cwe
===
"""
from CveXplore.common.data_source_connection import DatasourceConnection


class Cwe(DatasourceConnection):
    """
    Cwe database object
    """

    def __init__(self, **kwargs):

        super().__init__("cwe")

        for each in kwargs:
            setattr(self, each, kwargs[each])

    def iter_related_weaknessess(self):
        """
        Generator function for iterating the related weaknesses from the current weakness object

        :return: Cwe object
        :rtype: Cwe
        """
        if hasattr(self, "related_weaknesses"):
            if len(self.related_weaknesses) != 0:
                for each in self.related_weaknesses:

                    cwe_doc = self._datasource_connection.store_cwe.find_one(
                        {"id": each}
                    )

                    yield cwe_doc

    def iter_related_capecs(self):
        """
         Generator function for iterating the related capecs from the current weakness object

        :return: Capec object
        :rtype: Capec
        """

        related_capecs = self._datasource_connection.store_capec.find(
            {"related_weakness": self.id}
        )

        for each in related_capecs:
            yield each

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
        return "<< Cwe:{} >>".format(self.id)
