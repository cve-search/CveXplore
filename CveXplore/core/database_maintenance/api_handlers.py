import re
from typing import Union
from abc import abstractmethod

from CveXplore.common.cpe_converters import split_cpe_name
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

        self.missing_key_statistics = {}

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

    def safe_get(
        self, item: dict, dict_path: Union[list, str]
    ) -> Union[None, dict, list, str]:
        """Safely retrieve a value from a nested dictionary or list and track missing keys."""
        # Ensure dict_path is a list of keys (or indices)
        if isinstance(dict_path, str):
            keys = re.split(r"\.|\[|\]", dict_path)  # Split by '.' or '[' or ']'
            keys = [key for key in keys if key]
        else:
            keys = dict_path

        current_data = item

        for key in keys:
            if isinstance(current_data, list):
                # Handle list indices (e.g., [0]) by converting them to integers
                try:
                    key = int(key)
                    current_data = current_data[key]
                except (ValueError, IndexError):
                    self._record_missing_key(dict_path)
                    return None
            elif isinstance(current_data, dict):
                if key not in current_data:
                    self._record_missing_key(dict_path)
                    return None
                current_data = current_data[key]
            else:
                self._record_missing_key(dict_path)
                return None
        return current_data

    def _record_missing_key(self, dict_path: Union[list, str]) -> None:
        """Track missing keys with their path in the missing_key_statistics."""
        path_str = (
            ".".join(map(str, dict_path)) if isinstance(dict_path, list) else dict_path
        )
        self.missing_key_statistics[path_str] = (
            self.missing_key_statistics.get(path_str, 0) + 1
        )

    def log_statistics(self) -> None:
        """Log statistics for missing keys."""
        if self.missing_key_statistics:
            for path, count in self.missing_key_statistics.items():
                self.logger.warning(
                    f"Missing keys in processed data: {path} missing from {count} items"
                )
            self.missing_key_statistics.clear()

    @staticmethod
    def split_cpe_name(cpename: str) -> list[str]:
        return split_cpe_name(cpename)

    def stem(self, cpe_uri: str):
        cpe_stem = self.split_cpe_name(cpe_uri)
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
