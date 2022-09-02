import ee

ee.Initialize()

asset_parent = "projects/earthengine-legacy/assets/projects/deltares-rws/eo-bathymetry/test-collection"
asset_children = ee.data.listAssets({"parent": asset_parent})
for asset in asset_children["assets"]:
    ee.data.deleteAsset(asset["id"])
