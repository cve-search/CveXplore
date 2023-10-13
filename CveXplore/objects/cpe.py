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

    def iter_cves_matching_cpe(self, vuln_prod_search: bool = False):
        """
        Generator function for iterating over cve's matching this CPE. By default the search will be made matching
        the configuration fields of the cves documents.
        """

        cpe_searchField = (
            "vulnerable_product" if vuln_prod_search else "vulnerable_configuration"
        )

        # format to cpe2.3
        cpe_string = from2to3CPE(self.cpeName)

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

    def to_cve_summary(self, vuln_prod_search: bool = False) -> dict:
        """
        Method to request all cve's from the database based on this cpe object
        """
        all_cves = list(self.iter_cves_matching_cpe(vuln_prod_search=vuln_prod_search))
        data_cves = [
            d.to_dict(
                "id",
                "cvss",
                "cvss3",
                "published",
                "modified",
                "summary",
                "references",
                "status",
            )
            for d in all_cves
        ]
        data_cpe = self.to_dict()
        data_cpe["cvecount"] = len(data_cves)
        data_cpe["cves"] = data_cves
        return data_cpe

    def __repr__(self):
        """String representation of object"""
        return "<< Cpe:{} >>".format(self.id)
