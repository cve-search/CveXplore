"""
cves
====
"""
import datetime

from CveXplore.common.data_source_connection import DatasourceConnection


class Cves(DatasourceConnection):
    """
    Cves database object
    """

    def __init__(self, **kwargs):

        super().__init__("cves")

        for each in kwargs:
            setattr(self, each, kwargs[each])

        if hasattr(self, "cwe"):
            if isinstance(self.cwe, str):
                if self.cwe.lower() != "unknown":
                    cwe_id = self.cwe[4:]
                    # check if cwe_id can be cast to int
                    try:
                        if int(cwe_id):
                            results = getattr(
                                self._datasource_connection, "store_{}".format("cwe")
                            ).find_one({"id": cwe_id})
                            if results is not None:
                                self.cwe = results
                    except ValueError:
                        pass

                    capecs = self._datasource_connection.store_capec.find(
                        {"related_weakness": {"$in": [cwe_id]}}
                    )

                    setattr(self, "capec", list(capecs))

        via4s = self._datasource_connection.store_via4.find_one({"id": self.id})

        if via4s is not None:
            setattr(self, "via4_references", via4s)

    def iter_vuln_configurations(self):
        """
        Generator function for iterating over vulnerable configurations for this CVE.

        :return: vulnerable_configuration
        :rtype: str
        """

        if hasattr(self, "vulnerable_configuration"):
            for each in self.vulnerable_configuration:
                yield each

    def iter_references(self):
        """
        Generator function for iterating over references for this CVE.

        :return: references
        :rtype: str
        """

        if hasattr(self, "references"):
            for each in self.references:
                yield each

    def iter_capec(self):
        """
        Generator function for iterating over capecs for this CVE.

        :return: capec
        :rtype: Capec
        """

        if hasattr(self, "capec"):
            for each in self.capec:
                yield each

    def to_dict(self):
        """
        Method to convert the entire object to a dictionary

        :return: Data from object
        :rtype: dict
        """

        full_dict = {k: v for (k, v) in self.__dict__.items() if not k.startswith("_")}

        for k, v in full_dict.items():
            if isinstance(v, DatasourceConnection):
                full_dict[k] = v.to_dict()
            if isinstance(v, list):
                if len(v) > 0:
                    if isinstance(v[0], DatasourceConnection):
                        new_list = []
                        for each in v:
                            new_list.append(each.to_dict())
                        full_dict[k] = new_list
            if isinstance(v, datetime.datetime):
                full_dict[k] = str(v)

        return full_dict

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def __repr__(self):
        """ String representation of object """
        return "<< Cves:{} >>".format(self.id)
