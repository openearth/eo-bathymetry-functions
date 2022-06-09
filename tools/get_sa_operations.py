from json import dump
from pathlib import Path

import ee

service_account = "eo-bathymetry-automation@bathymetry.iam.gserviceaccount.com"
sa = ee.ServiceAccountCredentials(service_account, str(Path.cwd() / "gcloud_dist" / "eo-bathymetry-sa-key.json"))
ee.Initialize(sa)

ops = ee.data.listOperations()
with open("operations.json", "w") as f:
    dump(ops, f)
