"""
cpe
===
"""

from pymongo import DESCENDING

from CveXplore.common.cpe_converters import create_cpe_regex_string
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

        cpe_regex_string = create_cpe_regex_string(self.cpeName)

        results = self.datasource_connection.store_cves.find(
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
        return f"<< Cpe:{self.id} >>"
