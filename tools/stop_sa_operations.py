from json import dump
from pathlib import Path

import ee

service_account = "eo-bathymetry-automation@bathymetry.iam.gserviceaccount.com"
sa = ee.ServiceAccountCredentials(service_account, str(Path.cwd() / "gcloud_dist" / "key.json"))
ee.Initialize(sa)

ops = ee.data.listOperations()
for op in ops:
    ee.data.cancelOperation(op["name"])
