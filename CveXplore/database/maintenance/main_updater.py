from CveXplore.database.maintenance.Sources_process import (
    CPEDownloads,
    CVEDownloads,
    CWEDownloads,
    CAPECDownloads,
    VIADownloads,
    DatabaseIndexer,
)


class MainUpdater(object):
    def __init__(self, datasource, repopulate=False):

        self.datasource = datasource

        self.repopulate = repopulate

        self.sources = [
            {"name": "cpe", "updater": CPEDownloads},
            {"name": "cve", "updater": CVEDownloads},
            {"name": "cwe", "updater": CWEDownloads},
            {"name": "capec", "updater": CAPECDownloads},
            {"name": "via4", "updater": VIADownloads},
        ]

        self.posts = [{"name": "ensureindex", "updater": DatabaseIndexer}]

    def update(self):

        for source in self.sources:
            up = source["updater"]()
            up.update()

        for post in self.posts:
            indexer = post["updater"]()
            indexer.create_indexes()

        self.datasource.set_handlers_for_collections()

    def initialize(self):

        cpe_pop = CPEDownloads()
        cpe_pop.populate()

        cve_pop = CVEDownloads()
        cve_pop.populate()

        self.update()
