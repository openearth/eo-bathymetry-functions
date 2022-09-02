from ctypes import ArgumentError
from datetime import date as Date
from json import dumps
from typing import Any, Dict, List, Optional, Tuple
from re import sub

import ee
from eepackages.applications.bathymetry import Bathymetry
from eepackages import tiler
from googleapiclient.discovery import build

from eo_bathymetry_functions.utils import get_rolling_window_dates


LEGACY_ASSET_PREFIX: str = "projects/earthengine-legacy/assets"

def get_tile_bathymetry(tile: ee.Feature, start: ee.String, stop: ee.String) -> ee.Image:
    """
    Get subtidal bathymetry based on tile geometry.
    Server-side compliant for GEE.

    args:
        tile (ee.Feature): tile geometry used to obtain bathymetry.
        start (ee.String): start date in YYYY-MM-dd format.
        stop (ee.String): stop date in YYYY-MM-dd format.
    
    returns:
        ee.Image: image containing subtidal bathymetry covering tile.
    """

    bounds: ee.Geometry = ee.Feature(tile).geometry().bounds(1)
    sdb: Bathymetry = Bathymetry()
    zoom: ee.String = ee.String(tile.get("zoom"))
    tx: ee.String = ee.String(tile.get("tx"))
    ty: ee.String = ee.String(tile.get("ty"))
    tile_name: ee.String = ee.String("z").cat(zoom).cat("_x").cat(tx).cat("_y").cat(ty).replace("\.\d+", "", "g")
    img_fullname: ee.String = ee.String(tile_name).cat("_t").cat(ee.Date(start).millis().format())
    
    image: ee.Image = sdb.compute_inverse_depth(
                bounds=bounds,
                start=start,
                stop=stop,
                filter_masked=True,
                scale=tiler.zoom_to_scale(ee.Number.parse(tile.get("zoom"))).multiply(5),
    )
    image = image.set(
        "fullname", img_fullname,
        "system:time_start", ee.Date(start).millis(),
        "system:time_stop", ee.Date(stop).millis(),
        "zoom", zoom,
        "tx", tx,
        "ty", ty
    )
    return image

def tile_to_asset(
    image: ee.Image,
    tile: ee.Feature,
    export_scale: int,
    asset_path_prefix: str,
    asset_name: str,
    overwrite: bool,
    global_log_fields: Optional[Dict[str, str]] = None
) -> Optional[ee.batch.Task]:
    """
    Export a tile to a earth engine asset

    args:
        image (ee.Image): image to export
        tile (ee.Feature): tile that defines geometry
        export_scale (int): scale for the tile export
        asset_path_prefix (str): prefix of the asset path
        asset_name (str): name of the asset
        overwrite (bool): whether to overwrite any existing artifacts
        global_log_fields (Optional(Dict)): log fields for the entire cloud function.

    returns:
        Optional[ee.batch.Task] started task
    """
    if not global_log_fields:
        global_log_fields: Dict[str, str] = {}
    asset_id: str = f"{asset_path_prefix}/{asset_name}"
    asset: Dict[str, Any] = ee.data.getInfo(f"{LEGACY_ASSET_PREFIX}/{asset_id}")
    if overwrite and asset:
        print(dumps({
            "severity": "NOTICE",
            "message": f"deleting asset {asset_name}",
            **global_log_fields
        }))
        ee.data.deleteAsset(f"{LEGACY_ASSET_PREFIX}/{asset_id}")
    elif asset:
        print(dumps({
            "severity": "NOTICE",
            "message": f"asset {asset} already exists, skipping {asset_name}",
            **global_log_fields
        }))
        return

    bounds: ee.Geometry = tile.geometry().buffer(export_scale).bounds()
    task: ee.batch.Task = ee.batch.Export.image.toAsset(
        image,
        assetId=asset_id,
        description=asset_name,
        region=bounds,
        scale=export_scale,
        crs="EPSG:3857",
        maxPixels=1e10
    )
    task.start()
    print(dumps({
        "severity": "NOTICE",
        "message": f"exporting {asset_name} to {asset_id}, taskid: {task.id}",
        **global_log_fields
    }))

def tile_to_cloud_storage(
    image: ee.Image,
    tile: ee.Feature,
    export_scale: int,
    bucket: str,
    bucket_path: str,
    overwrite: bool,
    global_log_fields: Optional[Dict[str, str]] = None
) -> Optional[ee.batch.Task]:
    """
    Export a tile to cloud storage

    args:
        image (ee.Image): image to export
        tile (ee.Feature): tile that defines geometry
        export_scale (int): scale for the tile export
        bucket (str): name of the gcs bucket
        bucket_path (str): path to the object in the bucket
        overwrite (bool): whether to overwrite any existing artifacts
        global_log_fields (Optional(Dict)): log fields for the entire cloud function.

    returns:
        Optional[ee.batch.Task] started task
    """
    if not global_log_fields:
        global_log_fields: Dict[str, str] = {}
    with build('storage', 'v1') as storage:
        res = storage.objects().list(bucket=bucket, prefix="/".join(bucket_path.split("/")[:-1])).execute()
    if not overwrite:
        try:
            object_exists = any(map(lambda item: item.get("name").startswith(bucket_path), res.get("items")))
        except (AttributeError, TypeError):
            object_exists = False
        if object_exists:
            print(dumps({
                "severity": "NOTICE",
                "message": f"object {bucket_path} already exists in bucket {bucket}, skipping",
                **global_log_fields
            }))
            return
    
    bounds: ee.Geometry = tile.geometry().buffer(export_scale).bounds()
        
    task: ee.batch.Task = ee.batch.Export.image.toCloudStorage(
        image,
        bucket=bucket,
        description=bucket_path.replace("/", "_"),
        fileNamePrefix=bucket_path,
        region=bounds,
        scale=export_scale,
        crs="EPSG:3857",
        maxPixels=1e10
    )
    task.start()
    print(dumps({
        "severity": "NOTICE",
        "message": f"exporting tile to bucket {bucket}/{bucket_path}, taskid: {task.id}",
        **global_log_fields
    }))
    return task

def export_sdb_tiles(
    sink: str,
    tile_list: ee.List,
    num_tiles: int,
    export_scale: int,
    sdb_tiles: ee.ImageCollection,
    name_suffix: str,
    task_list: List[ee.batch.Task],
    overwrite: bool,
    bucket: Optional[str] = None,
    asset_path: Optional[str] = None,
    global_log_fields: Optional[Dict[str, str]] = None
) -> List[ee.batch.Task]:
    """
    Export list of tiled images containing subtidal bathymetry. Fires off the tasks and adds to the list of tasks.
    based on: https://github.com/gee-community/gee_tools/blob/master/geetools/batch/imagecollection.py#L166

    args:
        sink (str): type of data sink to export to. Viable options are: "asset" and "cloud".
        tile_list (ee.List): list of tile features.
        num_tiles (int): number of tiles in `tile_list`.
        export_scale (int): scale of the export product.
        sdb_tiles (ee.ImageCollection): collection of subtidal bathymetry images corresponding
            to input tiles.
        name_suffix (str): unique identifier after tile statistics.
        task_list (List[ee.batch.Task]): list of tasks, adds tasks created to this list.
        overwrite (bool): whether to overwrite the current assets under the same `asset_path`.
        bucket (Optional(str)): Bucket where the data is stored. Only used when sink = "cloud".
        asset_path (Optional(str)): Path where the asset will be stored. Only used when sink = "asset".
        global_log_fields (Optional(Dict)): log fields for the entire cloud function.
    
    returns:
        List[ee.batch.Task]: list of started tasks

    """
    if not global_log_fields:
        global_log_fields: Dict[str, str] = {}
    if sink == "asset":
        # create folder if not exists
        ee.data.create_assets(asset_ids=[asset_path], asset_type="Folder", mk_parents=True)
    
    for i in range(num_tiles):
        # get tile
        temp_tile: ee.Feature = ee.Feature(tile_list.get(i))
        tile_metadata: Dict[str, Any] = temp_tile.getInfo()["properties"]
        tx: str = tile_metadata["tx"]
        ty: str = tile_metadata["ty"]
        zoom: str = tile_metadata["zoom"]
        # filter imagecollection based on tile
        filtered_ic: ee.ImageCollection = sdb_tiles \
            .filterMetadata("tx", "equals", tx) \
            .filterMetadata("ty", "equals", ty) \
            .filterMetadata("zoom", "equals", zoom)
        # if filtered correctly, only a single image remains
        img: ee.Image = ee.Image(filtered_ic.first())  # have to cast here
        img_name: str = sub(r"\.\d+", "", f"z{zoom}/x{tx}/y{ty}/") + name_suffix
        # Export image
        if sink == "asset":  # Replace with case / switch in python 3.10
            task: Optional[ee.batch.Task] = tile_to_asset(
                image=img,
                tile=temp_tile,
                export_scale=export_scale,
                asset_path_prefix=asset_path,
                asset_name=img_name.replace("/", "_"),
                overwrite=overwrite,
                global_log_fields=global_log_fields
            )
            if task: task_list.append(task)
        elif sink == "cloud":
            if not bucket:
                raise ArgumentError("Sink option requires \"bucket\" arg.")
            task: ee.batch.Task = tile_to_cloud_storage(
                image=img,
                tile=temp_tile,
                export_scale=export_scale,
                bucket=bucket,
                bucket_path=img_name,
                overwrite=overwrite,
                global_log_fields=global_log_fields
            )
        else:
            raise ArgumentError("unrecognized data sink: {sink}")
        task_list.append(task)
    return task_list

def export_tiles(
    sink: str,
    geometry: ee.Geometry,
    zoom: int,
    export_zoom: Optional[int] = None,
    start: Optional[str] = None,
    stop: Optional[str] = None,
    step_months: int = 3,
    window_years: int = 2,
    overwrite: Optional[bool] = False,
    bucket: Optional[str] = None,
    asset_path: Optional[str] = None,
    global_log_fields: Optional[Dict[str, str]] = None
) -> None:
    """
    From a geometry, creates tiles of input zoom level, calculates subtidal bathymetry in those
    tiles, and exports those tiles.

    args:
        sink (str): type of data sink to export to. Viable options are: "asset" and "cloud".
        geometry (ee.Geometry): geometry of the area of interest.
        zoom (int): zoom level of the to-be-exported tiles.
        export_zoom (int): zoom level for determining resolution of export tiles.
        start (ee.String): start date in YYYY-MM-dd format, defaults to one timestep before stop.
        stop (ee.String): stop date in YYYY-MM-dd format, defaults to start of this month
        step_months (int): steps with which to roll the window over which the subtidal bathymetry
            is calculated.
        window_years (int): number of years over which the subtidal bathymetry is calculated.
        overwrite (bool): whether to overwrite current tiles in the sink.
        bucket (Optional(str)): bucket for sink "cloud".
        asset_path (Optional(str)): Path where the asset will be stored. Only used when sink = "asset".
        global_log_fields (Optional(Dict)): log fields for the entire cloud function.
    """
    if not global_log_fields:
        global_log_fields: Dict[str, str] = {}
    
    if not export_zoom:
        export_zoom = zoom
    
    dates: List[Tuple[Date]] = get_rolling_window_dates(start, stop, step_months, window_years)
    
    # Get tiles
    tiles: ee.FeatureCollection = tiler.get_tiles_for_geometry(geometry, ee.Number(zoom))

    scale: float = tiler.zoom_to_scale(export_zoom).getInfo()
    task_list: List[ee.batch.Task] = []
    num_tiles: int = tiles.size().getInfo()
    tile_list: ee.List = tiles.toList(num_tiles)

    for date in dates:
        sdb_tiles: ee.ImageCollection = tiles.map(
            lambda tile: get_tile_bathymetry(
                tile=tile,
                start=ee.String(date[0]),
                stop=ee.String(date[1])
            )
        )

        # Now export tiles
        export_sdb_tiles(
            sink=sink,
            tile_list=tile_list,
            num_tiles=num_tiles,
            export_scale=scale,
            sdb_tiles=sdb_tiles,
            name_suffix=f"t{date[0]}_{date[1]}",
            task_list=task_list,
            overwrite=overwrite,
            bucket=bucket,
            asset_path=asset_path,
            global_log_fields=global_log_fields
        )
