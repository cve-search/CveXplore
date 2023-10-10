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
from CveXplore.errors import UpdateSourceNotFound

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

    def update(self, update_source: str | list = None):
        """
        Method used for updating the database
        """
        if not isinstance(update_source, str | list):
            raise ValueError
        try:
            if update_source is None:

                for source in self.sources:
                    up = source["updater"]()
                    up.update()

            elif isinstance(update_source, list):
                for source in update_source:
                    try:
                        update_this_source = [
                            x for x in self.sources if x["name"] == source
                        ][0]
                        up = update_this_source["updater"]()
                        up.update()
                    except IndexError:
                        raise UpdateSourceNotFound(
                            f"Provided source: {source} could not be found...."
                        )
            else:
                # single string then....
                try:
                    update_this_source = [
                        x for x in self.sources if x["name"] == update_source
                    ][0]
                    up = update_this_source["updater"]()
                    up.update()
                except IndexError:
                    raise UpdateSourceNotFound(
                        f"Provided source: {update_source} could not be found...."
                    )
        except UpdateSourceNotFound:
            raise
        else:
            for post in self.posts:
                indexer = post["updater"]()
                indexer.create_indexes()

        self.datasource.set_handlers_for_collections()

        self.logger.info(f"Database update / initialization complete!")

    def populate(self, populate_source: str | list = None):
        """
        Method used for updating the database
        """
        if not isinstance(populate_source, str | list):
            raise ValueError
        try:
            if populate_source is None:
                for source in self.sources:
                    up = source["updater"]()
                    up.populate()

            elif isinstance(populate_source, list):
                for source in populate_source:
                    try:
                        update_this_source = [
                            x for x in self.sources if x["name"] == source
                        ][0]
                        up = update_this_source["updater"]()
                        up.populate()
                    except IndexError:
                        raise UpdateSourceNotFound(
                            f"Provided source: {source} could not be found...."
                        )
            else:
                # single string then....
                try:
                    update_this_source = [
                        x for x in self.sources if x["name"] == populate_source
                    ][0]
                    up = update_this_source["updater"]()
                    up.populate()
                except IndexError:
                    raise UpdateSourceNotFound(
                        f"Provided source: {populate_source} could not be found...."
                    )
        except UpdateSourceNotFound:
            raise
        else:
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
