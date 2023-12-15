import logging

import ijson

from CveXplore.core.database_maintenance.update_base_class import UpdateBaseClass
from CveXplore.core.logging.logger_class import AppLogger

logging.setLoggerClass(AppLogger)


class IJSONHandler(UpdateBaseClass):
    def __init__(self):
        super().__init__(__name__)

    def fetch(self, filename: str, prefix: str):
        x = 0
        with open(filename, "rb") as input_file:
            for item in ijson.items(input_file, prefix):
                yield item
                x += 1

        self.logger.debug(
            f"Processed {x} items from file: {filename}, using prefix: {prefix}"
        )
