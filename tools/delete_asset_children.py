# Script to run delete the children of a given asset
# Usage: python delete_asset_children.py
# TODO: currently used with manual code commenting / editing, should become cli utility.

import ee

ee.Initialize()

LEGACY_ASSET_PREFIX: str = "projects/earthengine-legacy/assets"

asset_parent = (
    f"{LEGACY_ASSET_PREFIX}/projects/deltares-rws/eo-bathymetry/depth-uncalibrated-nl"
)
asset_children = ee.data.listAssets({"parent": asset_parent})
for asset in asset_children["assets"]:
    # asset_children2 = ee.data.listAssets({"parent": asset["name"]})["assets"]
    # for asset2 in asset_children2:
    #     ee.data.deleteAsset(asset2["name"])
    ee.data.deleteAsset(asset["name"])
ee.data.deleteAsset(asset_parent)
