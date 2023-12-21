import json
import os

from CveXplore.common.config import Configuration
from CveXplore.core.database_maintenance.sources_process import CVEDownloads
from CveXplore.core.nvd_nist.nvd_nist_api import NvdNistApi

config = Configuration

os.environ["MONGODB_CON_DETAILS"] = json.dumps(
    {
        "host": f"{config.DATASOURCE_PROTOCOL}://{config.MONGODB_HOST}:{config.MONGODB_PORT}"
    }
)

cvd = CVEDownloads()

nvd = NvdNistApi()

cvd.is_update = False

data = nvd.call(nvd.methods.GET, resource={"cveId": "CVE-2016-2148"}, data=1)

cvd.process_the_item(data["vulnerabilities"][0])
