import json
import os

from CveXplore.api.nvd_nist.nvd_nist_api import NvdNistApi
from CveXplore.common.config import Configuration
from CveXplore.database.maintenance.Sources_process import CVEDownloads

config = Configuration()

os.environ["MONGODB_CON_DETAILS"] = json.dumps(
    {"host": f"mongodb://{config.MONGODB_HOST}:{config.MONGODB_PORT}"}
)

cvd = CVEDownloads()

nvd = NvdNistApi()

cvd.is_update = False

data = nvd.call(nvd.methods.GET, resource={"cveId": "CVE-2016-2148"}, data=1)

cvd.process_the_item(data["vulnerabilities"][0])
