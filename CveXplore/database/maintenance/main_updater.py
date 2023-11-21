"""
Main Updater
============
"""
import logging
import time
from datetime import timedelta

from CveXplore.database.maintenance.DatabaseSchemaChecker import SchemaChecker
from CveXplore.database.maintenance.LogHandler import UpdateHandler
from CveXplore.database.maintenance.Sources_process import (
    CPEDownloads,
    CVEDownloads,
    CWEDownloads,
    CAPECDownloads,
    VIADownloads,
    EPSSDownloads,
    DatabaseIndexer,
)
from CveXplore.errors import UpdateSourceNotFound

logging.setLoggerClass(UpdateHandler)


class MainUpdater(object):
    """
    The MainUpdater class is the main class for performing database maintenance tasks
    """

    def __init__(self, datasource):
        """
        Init a new MainUpdater class
        """

        self.datasource = datasource

        self.sources = [
            {"name": "cpe", "updater": CPEDownloads},
            {"name": "cve", "updater": CVEDownloads},
            {"name": "cwe", "updater": CWEDownloads},
            {"name": "capec", "updater": CAPECDownloads},
            {"name": "via4", "updater": VIADownloads},
            {"name": "epss", "updater": EPSSDownloads},
        ]

        self.posts = [
            {"name": "ensureindex", "updater": DatabaseIndexer},
            {"name": "schema", "updater": SchemaChecker},
        ]

        self.schema_checker = SchemaChecker()

        self.logger = logging.getLogger(__name__)

    def validate_schema(self):
        return self.schema_checker.validate_schema()

    def update(self, update_source: str | list = None):
        """
        Method used for updating the database
        """
        self.logger.info(f"Starting Database update....")
        start_time = time.time()

        if update_source is not None:
            if not isinstance(update_source, str | list):
                raise ValueError("Wrong 'update_source' parameter type received!")

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

        self.logger.info(f"Database update complete!")
        self.logger.info(
            f"Update Total duration: {timedelta(seconds=time.time() - start_time)}"
        )

    def populate(self, populate_source: str | list = None):
        """
        Method used for updating the database
        """
        self.logger.info(f"Starting Database population....")
        start_time = time.time()

        if populate_source is not None:
            if not isinstance(populate_source, str | list):
                raise ValueError("Wrong 'populate_source' parameter type received!")

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

        self.logger.info(f"Database population complete!")
        self.logger.info(
            f"Populate total duration: {timedelta(seconds=time.time() - start_time)}"
        )

    def initialize(self):
        """
        Method to initialize a new (fresh) instance of a cvedb database
        """

        self.logger.info(f"Starting Database initialization....")
        start_time = time.time()

        cpe_pop = CPEDownloads()
        cpe_pop.populate()

        self.logger.info(
            f"Sleeping for 30 seconds between CPE and CVE database population.."
        )
        time.sleep(30)

        cve_pop = CVEDownloads()
        cve_pop.populate()

        self.update()

        self.logger.info(f"Database initialization complete!")
        self.logger.info(
            f"Initialization total duration: {timedelta(seconds=time.time() - start_time)}"
        )
