"""
CPE Converters
==============
"""
from CveXplore.database.helpers.cpe_conversion import cpe_uri_to_fs, cpe_fs_to_uri


def from2to3CPE(cpe: str, autofill: bool = False) -> str:
    """
    Method to transform cpe2.2 to cpe2.3 format
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


def from3to2CPE(cpe: str) -> str:
    """
    Method to transform cpe2.3 to cpe2.2 format
    """
    cpe = cpe.strip()
    if not cpe.startswith("cpe:/"):
        if not cpe.startswith("cpe:2.3:"):
            return False
        cpe = cpe_fs_to_uri(cpe)
    return cpe
