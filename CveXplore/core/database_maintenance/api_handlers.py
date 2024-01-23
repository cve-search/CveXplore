from abc import abstractmethod

from CveXplore.core.database_actions.db_action import DatabaseAction
from CveXplore.core.database_maintenance.download_handler import DownloadHandler
from CveXplore.core.nvd_nist.nvd_nist_api import NvdNistApi


class NVDApiHandler(DownloadHandler):
    """
    This class handles all JSON related download processing and functions as a base class for specific JSON sources
    processing and downloading
    """

    def __init__(self, feed_type: str, logger_name: str):
        super().__init__(feed_type=feed_type, logger_name=logger_name)

        self.is_update = True

        self.api_handler = NvdNistApi(proxies=self.config.HTTP_PROXY_DICT)

    def process_item(self, item: dict):
        item = self.process_the_item(item)

        if item is not None:
            if self.is_update:
                return DatabaseAction(
                    action=DatabaseAction.actions.UpdateOne,
                    doc=item,
                ).entry
            else:
                # return DatabaseAction(
                #     action=DatabaseAction.actions.InsertOne,
                #     doc=item,
                # ).entry
                return item

    @staticmethod
    def stem(cpe_uri: str):
        cpe_stem = cpe_uri.split(":")
        return ":".join(cpe_stem[:5])

    @staticmethod
    def padded_version(version: str):
        if version == "-" or version == "":
            return version
        else:
            # normalizing edge cases:
            version = version.replace("\\(", ".").replace("\\)", ".").rstrip(".")

            ret_list = []

            splitted_version = version.split(".")
            # perform check if last part of version can be cast to an int
            try:
                int(splitted_version[-1])
                # can be cast to an int, proceed 'normally'
                for v in splitted_version:
                    try:
                        ret_list.append(f"{int(v):05d}")
                    except ValueError:
                        ret_list.append(v.rjust(5, "0"))
            except ValueError:
                # last part of the version cannot be cast to an int, so this means it's either a string or a
                # string combined with an integer; handle accordingly

                # first handle all version identifiers leading upto the last part
                if len(splitted_version) > 1:
                    for i in range(len(splitted_version) - 1):
                        try:
                            ret_list.append(f"{int(splitted_version[i]):05d}")
                        except ValueError:
                            ret_list.append(splitted_version[i].rjust(5, "0"))

                # handle the last part
                # check if the last entry is smaller than 5 characters, if so just use that...
                if len(splitted_version[-1]) > 5:
                    try:
                        ret_list.append(f"{int(splitted_version[-1]):05d}")
                    except ValueError:
                        ret_list.append(splitted_version[-1].rjust(5, "0"))
                # check is last entry consists only of alphanumeric characters
                elif splitted_version[-1].isalpha():
                    ret_list.append(splitted_version[-1].rjust(5, "0"))
                else:
                    loop_i = 0
                    loop_count = len(splitted_version[-1])

                    # int/str combined value; handle accordingly
                    while loop_i < loop_count:
                        current_i = loop_i
                        # probably digit; so check;
                        if splitted_version[-1][loop_i].isdigit():
                            try:
                                ret_list.append(
                                    f"{int(splitted_version[-1][loop_i]):05d}"
                                )
                            except ValueError:
                                ret_list.append(
                                    splitted_version[-1][loop_i].rjust(5, "0")
                                )
                            finally:
                                # perform check if anything that follows consists only of string characters
                                if splitted_version[-1][loop_i + 1 :].isalpha():
                                    ret_list.append(
                                        splitted_version[-1][loop_i + 1 :].rjust(5, "0")
                                    )
                                    # no point proceeding; just break
                                    break
                                loop_i += 1
                        else:
                            # ok so probably last part of version identifier is a string; add that with a loop
                            version_string = ""
                            try:
                                while splitted_version[-1][loop_i].isalpha():
                                    version_string += splitted_version[-1][loop_i]
                                    loop_i += 1
                            except IndexError:
                                # finished splitted_version variable; just pass
                                loop_i += 1
                                pass

                            ret_list.append(version_string.rjust(5, "0"))

                        if loop_i == current_i:
                            loop_i += 1

            return ".".join(ret_list)

    @abstractmethod
    def process_the_item(self, *args):
        raise NotImplementedError

    @abstractmethod
    def file_to_queue(self, *args):
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def populate(self, **kwargs):
        raise NotImplementedError
