import logging
import os
from logging.handlers import RotatingFileHandler

import colors

from CveXplore.common.config import Configuration
from CveXplore.core.logging.formatters.task_formatter import TaskFormatter
from CveXplore.core.logging.handlers.gelf_handler import GelfUDPHandler
from CveXplore.core.logging.handlers.syslog_handler import FullSysLogHandler

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

level_map = {
    "debug": "magenta",
    "info": "white",
    "warning": "yellow",
    "error": "red",
    "critical": "red",
}


class AppLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        self.formatter = TaskFormatter(
            "%(asctime)s - %(task_name)s - %(name)-8s - %(levelname)-8s - [%(task_id)s] %(message)s"
        )
        self.config = Configuration

        root = logging.getLogger()

        root.setLevel(logging.DEBUG)

        root_null_handler = logging.NullHandler()
        root.handlers.clear()
        root.addHandler(root_null_handler)

        super().__init__(name, level)

        self.propagate = False

        if self.config.LOGGING_FILE_PATH != "":
            if not os.path.exists(self.config.LOGGING_FILE_PATH):
                os.makedirs(self.config.LOGGING_FILE_PATH)

            crf = RotatingFileHandler(
                filename=f"{self.config.LOGGING_FILE_PATH}/{self.config.LOGGING_FILE_NAME}",
                maxBytes=self.config.LOGGING_MAX_FILE_SIZE,
                backupCount=self.config.LOGGING_BACKLOG,
            )
            crf.setLevel(self.config.LOGGING_LEVEL)
            crf.setFormatter(self.formatter)
            self.addHandler(crf)

        if self.config.SYSLOG_ENABLE:
            syslog_server = self.config.SYSLOG_SERVER
            syslog_port = self.config.SYSLOG_PORT

            if self.config.GELF_SYSLOG:
                syslog = GelfUDPHandler(
                    host=syslog_server,
                    port=syslog_port,
                    _application_name="CveXplore",
                    include_extra_fields=True,
                    debug=True,
                    **self.config.GELF_SYSLOG_ADDITIONAL_FIELDS
                    if self.config.GELF_SYSLOG_ADDITIONAL_FIELDS is not None
                    else {},
                )
            else:
                syslog = FullSysLogHandler(
                    address=(syslog_server, syslog_port),
                    facility=FullSysLogHandler.LOG_LOCAL0,
                    appname="CveXplore",
                )

            syslog.setFormatter(self.formatter)
            syslog.setLevel(self.config.SYSLOG_LEVEL)
            self.addHandler(syslog)

    def debug(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘DEBUG’ and color *MAGENTA.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.debug(“Houston, we have a %s”, “thorny problem”, exc_info=1)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=level_map["debug"])

        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘INFO’ and color *WHITE*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.info(“Houston, we have a %s”, “interesting problem”, exc_info=1)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=level_map["info"])

        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘WARNING’ and color *YELLOW*.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.warning(“Houston, we have a %s”, “bit of a problem”, exc_info=1)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=level_map["warning"])

        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘ERROR’ and color *RED*.

        Store logged message to the database for dashboard alerting.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.error(“Houston, we have a %s”, “major problem”, exc_info=1)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=level_map["error"])

        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log ‘msg % args’ with severity ‘CRITICAL’ and color *RED*.

        Store logged message to the database for dashboard alerting.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.critical(“Houston, we have a %s”, “hell of a problem”, exc_info=1)

        :param msg: Message to log
        :type msg: str
        """

        msg = colors.color("{}".format(msg), fg=level_map["critical"])

        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)
