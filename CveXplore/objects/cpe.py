"""
cpe
===
"""
import re

from pymongo import DESCENDING

from CveXplore.common.cpe_converters import from2to3CPE
from CveXplore.common.data_source_connection import DatasourceConnection


class Cpe(DatasourceConnection):
    """
    Cpe database object
    """

    def __init__(self, **kwargs):

        super().__init__("cpe")

        for each in kwargs:
            setattr(self, each, kwargs[each])

    def iter_cves_matching_cpe(self, vuln_prod_search=False):
        """
        Generator function for iterating over cve's matching this CPE. By default the search will be made matching
        the configuration fields of the cves documents.

        :param vuln_prod_search: Search for matching products instead of configurations
        :type vuln_prod_search: bool
        :return: Matching CVES
        :rtype: Cves
        """

        cpe_searchField = (
            "vulnerable_product" if vuln_prod_search else "vulnerable_configuration"
        )

        # format to cpe2.3
        cpe_string = from2to3CPE(self.cpe_2_2)

        if cpe_string.startswith("cpe"):
            # strict search with term starting with cpe; e.g: cpe:2.3:o:microsoft:windows_7:*:sp1:*:*:*:*:*:*

            remove_trailing_regex_stars = r"(?:\:|\:\:|\:\*)+$"

            cpe_regex = re.escape(re.sub(remove_trailing_regex_stars, "", cpe_string))

            cpe_regex_string = r"^{}:".format(cpe_regex)
        else:
            # more general search on same field; e.g. microsoft:windows_7
            cpe_regex_string = "{}".format(re.escape(cpe_string))

        results = self._datasource_connection.store_cves.find(
            {cpe_searchField: {"$regex": cpe_regex_string}}
        ).sort("cvss", DESCENDING)

        for each in results:
            if each is not None:
                yield each
            else:
                yield None

    def iter_cpe_names(self):
        """
        Generator function for iterating over cpe_names for this CPE.

        :return: cpe_name
        :rtype: str
        """

        if hasattr(self, "cpe_name"):
            for each in self.cpe_name:
                yield each
        else:
            return "None"

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
        return "<< Cpe:{} >>".format(self.id)
