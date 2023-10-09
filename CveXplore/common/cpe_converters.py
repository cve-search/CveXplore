"""
CPE Converters
==============
"""
from CveXplore.database.helpers.cpe_conversion import cpe_uri_to_fs, cpe_fs_to_uri


def from2to3CPE(cpe, autofill=False):
    """
    Method to transform cpe2.2 to cpe2.3 format

    :param cpe: cpe2.2 string
    :type cpe: str
    :param autofill: Whether to cpe string should be autofilled with double quotes and hyphens
    :type autofill: bool
    :return: cpe2.3 formatted string
    :rtype: str
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:2.3:"):
        if not cpe.startswith("cpe:/"):
            return False
        cpe = cpe_uri_to_fs(cpe)
    if autofill:
        e = cpe.split(":")
        for x in range(0, 13 - len(e)):
            cpe += ":-"
    return cpe


def from3to2CPE(cpe):
    """
    Method to transform cpe2.3 to cpe2.2 format

    :param cpe: cpe2.3 string
    :type cpe: str
    :return: cpe2.2 string
    :rtype: str
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:/"):
        if not cpe.startswith("cpe:2.3:"):
            return False
        cpe = cpe_fs_to_uri(cpe)
    return cpe


def pad(seq, target_length, padding=None):
    length = len(seq)
    if length > target_length:
        return seq
    seq.extend([padding] * (target_length - length))
    return seq
