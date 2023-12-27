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
                    cwe_doc = self.datasource_connection.store_cwe.find_one(
                        {"id": each}
                    )

                    yield cwe_doc

    def iter_related_capecs(self):
        """
         Generator function for iterating the related capecs from the current weakness object

        :return: Capec object
        :rtype: Capec
        """

        related_capecs = self.datasource_connection.store_capec.find(
            {"related_weakness": self.id}
        )

        for each in related_capecs:
            yield each

    def __repr__(self):
        """String representation of object"""
        return f"<< Cwe:{self.id} >>"
