import logging
import sys

from CveXplore.common.config import Configuration
from CveXplore.core.logging.handlers.cve_explore_rfh import CveExploreUpdateRfhHandler
from CveXplore.core.logging.handlers.cve_explore_stream import (
    CveExploreUpdateStreamHandler,
)


class UpdateBaseClass(object):
    def __init__(self, logger_name: str):
        self.config = Configuration
        self.logger = logging.getLogger(logger_name)

        if len(self.logger.handlers) == 1:
            self.logger.removeHandler(self.logger.handlers[0])

        self.logger.propagate = False

        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        crf = None

        cli = CveExploreUpdateStreamHandler(stream=sys.stdout)
        cli.setFormatter(self.formatter)
        cli.setLevel(logging.INFO)

        if self.config.LOGGING_TO_FILE:
            crf = CveExploreUpdateRfhHandler(
                filename=f"{self.config.LOGGING_FILE_PATH}/{self.config.LOGGING_UPDATE_FILE_NAME}",
                maxBytes=self.config.LOGGING_MAX_FILE_SIZE,
                backupCount=self.config.LOGGING_BACKLOG,
            )
            crf.setLevel(logging.DEBUG)
            crf.setFormatter(self.formatter)

        if len(self.logger.handlers) > 0:
            for handler in self.logger.handlers:
                # add the handlers to the logger
                # makes sure no duplicate handlers are added
                if not isinstance(
                    handler, CveExploreUpdateRfhHandler
                ) and not isinstance(handler, CveExploreUpdateStreamHandler):
                    if crf is not None:
                        self.logger.addHandler(crf)
                    self.logger.addHandler(cli)
        else:
            if crf is not None:
                self.logger.addHandler(crf)
            self.logger.addHandler(cli)
