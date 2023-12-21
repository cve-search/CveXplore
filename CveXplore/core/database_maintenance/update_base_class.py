import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from CveXplore.common.config import Configuration


class UpdateBaseClass(object):
    def __init__(self, logger_name: str):
        self.config = Configuration
        self.logger = logging.getLogger(logger_name)

        self.logger.removeHandler(self.logger.handlers[0])

        self.logger.propagate = False

        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        crf = None

        cli = logging.StreamHandler(stream=sys.stdout)
        cli.setFormatter(self.formatter)
        cli.setLevel(logging.INFO)

        if self.config.LOGGING_FILE_PATH != "":
            if not os.path.exists(self.config.LOGGING_FILE_PATH):
                os.makedirs(self.config.LOGGING_FILE_PATH)

            crf = RotatingFileHandler(
                filename=f"{self.config.LOGGING_FILE_PATH}/{self.config.LOGGING_UPDATE_FILE_NAME}",
                maxBytes=self.config.LOGGING_MAX_FILE_SIZE,
                backupCount=self.config.LOGGING_BACKLOG,
            )
            crf.setLevel(logging.DEBUG)
            crf.setFormatter(self.formatter)

        if not len(self.logger.handlers):
            if crf is not None:
                self.logger.addHandler(crf)
            self.logger.addHandler(cli)
