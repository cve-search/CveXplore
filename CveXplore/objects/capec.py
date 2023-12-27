"""
capec
=====
"""
from CveXplore.common.data_source_connection import DatasourceConnection


class Capec(DatasourceConnection):
    """
    Capec database object
    """

    def __init__(self, **kwargs):
        super().__init__("capec")

        for each in kwargs:
            setattr(self, each, kwargs[each])

    def iter_related_weaknessess(self):
        """
        Generator function for iterating the related weaknesses from the current Capec object

        :return: Cwe object
        :rtype: Cwe
        """
        if hasattr(self, "related_weakness"):
            if len(self.related_weakness) != 0:
                for each in self.related_weakness:
                    cwe_doc = self.datasource_connection.store_cwe.find_one(
                        {"id": each}
                    )

                    yield cwe_doc

    def iter_related_capecs(self):
        """
        Generator function for iterating the related capecs from the current Capec object

        :return: Capec objects
        :rtype: Capec
        """
        if hasattr(self, "related_capecs"):
            if len(self.related_capecs) != 0:
                for each in self.related_capecs:
                    capec_doc = self.datasource_connection.store_capec.find_one(
                        {"id": each}
                    )

                    yield capec_doc

    def __repr__(self):
        """String representation of object"""
        return f"<< Capec:{self.id} >>"
