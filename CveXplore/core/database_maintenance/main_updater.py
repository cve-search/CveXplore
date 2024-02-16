"""
Main Updater
============
"""
import logging
import time
from datetime import timedelta

from CveXplore.core.database_indexer.db_indexer import DatabaseIndexer
from CveXplore.core.database_maintenance.sources_process import (
    CPEDownloads,
    CVEDownloads,
    CWEDownloads,
    CAPECDownloads,
    VIADownloads,
    EPSSDownloads,
)
from CveXplore.core.database_maintenance.update_base_class import UpdateBaseClass
from CveXplore.core.database_migration.database_migrator import DatabaseMigrator
from CveXplore.core.database_version.db_version_checker import DatabaseVersionChecker
from CveXplore.core.logging.logger_class import AppLogger
from CveXplore.database.connection.base.db_connection_base import DatabaseConnectionBase
from CveXplore.errors import UpdateSourceNotFound

logging.setLoggerClass(AppLogger)


class MainUpdater(UpdateBaseClass):
    """
    The MainUpdater class is the main class for performing database database_maintenance tasks
    """

    def __init__(self, datasource: DatabaseConnectionBase, datasource_type: str):
        """
        Init a new MainUpdater class
        """
        super().__init__(logger_name=__name__)

        self.datasource = datasource
        self.datasource_type = datasource_type

        self.sources = [
            {"name": "cpe", "updater": CPEDownloads},
            {"name": "cve", "updater": CVEDownloads},
            {"name": "cwe", "updater": CWEDownloads},
            {"name": "capec", "updater": CAPECDownloads},
            {"name": "via4", "updater": VIADownloads},
            {"name": "epss", "updater": EPSSDownloads},
        ]

        self.database_indexer = DatabaseIndexer(datasource=datasource)
        self.schema_checker = DatabaseVersionChecker(datasource=datasource)
        self.database_migrator = DatabaseMigrator()

        self.do_initialize = False

    def __repr__(self):
        return f"<<MainUpdater>>"

    def validate_schema(self):
        return self.schema_checker.validate_schema()

    def update(self, update_source: str | list = None):
        """
        Method used for updating the database
        """
        self.logger.info(f"Starting Database update....")
        start_time = time.time()

        if not self.do_initialize:
            if self.datasource_type != "api" and self.datasource_type != "mongodb":
                self.logger.info(
                    f"Upgrading database schema to latest head, if needed..."
                )
                self.database_migrator.db_upgrade()

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

        self.database_indexer.create_indexes()

        self.schema_checker.update()

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

        if self.datasource_type != "api" and self.datasource_type != "mongodb":
            self.logger.info(f"Upgrading database schema to latest head, if needed...")
            self.database_migrator.db_upgrade()

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

        self.database_indexer.create_indexes()

        self.schema_checker.update()

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

        self.do_initialize = True

        if self.datasource_type != "api" and self.datasource_type != "mongodb":
            self.logger.info(f"Upgrading database schema to latest head, if needed...")
            self.database_migrator.db_upgrade()

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
