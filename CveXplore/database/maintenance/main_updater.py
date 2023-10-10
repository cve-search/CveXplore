"""
Main Updater
============
"""
import logging
import time

from CveXplore.database.maintenance.DatabaseSchemaChecker import SchemaChecker
from CveXplore.database.maintenance.LogHandler import UpdateHandler
from CveXplore.database.maintenance.Sources_process import (
    CPEDownloads,
    CVEDownloads,
    CWEDownloads,
    CAPECDownloads,
    VIADownloads,
    DatabaseIndexer,
)

logging.setLoggerClass(UpdateHandler)


class MainUpdater(object):
    """
    The MainUpdater class is the main class for performing database maintenaince tasks
    """

    def __init__(self, datasource):
        """
        Init a new MainUpdater class

        :param datasource: Datasource to update
        :type datasource: MongoDBConnection
        """

        self.datasource = datasource

        self.sources = [
            {"name": "cpe", "updater": CPEDownloads},
            {"name": "cve", "updater": CVEDownloads},
            {"name": "cwe", "updater": CWEDownloads},
            {"name": "capec", "updater": CAPECDownloads},
            {"name": "via4", "updater": VIADownloads},
        ]

        self.posts = [
            {"name": "ensureindex", "updater": DatabaseIndexer},
            {"name": "schema", "updater": SchemaChecker},
        ]

        self.logger = logging.getLogger("MainUpdater")

    def update(self):
        """
        Method used for updating the database
        """

        for source in self.sources:
            up = source["updater"]()
            up.update()

        for post in self.posts:
            indexer = post["updater"]()
            indexer.create_indexes()

        self.datasource.set_handlers_for_collections()

        self.logger.info(f"Database update / initialization complete!")

    def initialize(self):
        """
        Method to initialize a new (fresh) instance of a cvedb database
        """

        cpe_pop = CPEDownloads()
        cpe_pop.populate()

        self.logger.info(
            f"Sleeping for 30 seconds between CPE and CVE database population.."
        )
        time.sleep(30)

        cve_pop = CVEDownloads()
        cve_pop.populate()

        self.update()
