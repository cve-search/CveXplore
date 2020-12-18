from CveXplore.objects.capec import Capec
from CveXplore.objects.cpe import Cpe
from CveXplore.objects.cves import Cves
from CveXplore.objects.cwe import Cwe
from CveXplore.objects.via4 import Via4

database_objects_mapping = {
    "capec": Capec,
    "cpe": Cpe,
    "cwe": Cwe,
    "via4": Via4,
    "cves": Cves,
}
