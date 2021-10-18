from ctypes import ArgumentError
from functools import partial
from logging import Logger, getLogger
from typing import Any, Dict, List, Optional
from re import sub

from dateutil.parser import parse
import ee
from eepackages.applications.bathymetry import Bathymetry
from eepackages import tiler
from googleapiclient.discovery import build

logger: Logger = getLogger(__name__)

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
    overwrite: bool
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

    returns:
        Optional[ee.batch.Task] started task
    """
    asset_id: str = f"{asset_path_prefix}/{asset_name}"
    asset: Dict[str, Any] = ee.data.getInfo(asset_id)
    if overwrite and asset:
        logger.info(f"deleting asset {asset}")
        ee.data.deleteAsset(asset_id)
    elif asset:
        logger.info(f"asset {asset} already exists, skipping {asset_name}")
        return
    task: ee.batch.Task = ee.batch.Export.image.toAsset(
        image,
        assetId=asset_id,
        description=asset_name,
        region=tile.geometry(),
        scale=export_scale
    )
    task.start()
    logger.info(f"exporting {asset_name} to {asset_id}")

def tile_to_cloud_storage(
    image: ee.Image,
    tile: ee.Feature,
    export_scale: int,
    bucket: str,
    bucket_path: str,
    overwrite: bool
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

    returns:
        Optional[ee.batch.Task] started task
    """
    with build('storage', 'v1') as storage:
        res = storage.objects().list(bucket=bucket, prefix="/".join(bucket_path.split("/")[:-1])).execute()
    if not overwrite:
        try:
            object_exists = any(map(lambda item: item.get("name").startswith(bucket_path), res.get("items")))
        except AttributeError:
            object_exists = False
        if object_exists:
            logger.info(f"object {bucket_path} already exists in bucket {bucket}, skipping")
            return
        
    task: ee.batch.Task = ee.batch.Export.image.toCloudStorage(
        image,
        bucket=bucket,
        description=bucket_path,
        fileNamePrefix=bucket_path,
        region=tile.geometry(),
        scale=export_scale
    )
    task.start()
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
    bucket: Optional[str] = None
) -> List[ee.batch.Task]:
    """
    Export list of tiled images containing subtidal bathymetry. Fires off the tasks and adds to the list of tasks.
    based on: https://github.com/gee-community/gee_tools/blob/master/geetools/batch/imagecollection.py#L166

    args:
        sink (str): type of data sink to export to. Viable options are: "asset" and "cloud".
        tile_list (ee.List): list of tile features.
        num_tiles (int): number of tiles in `tile_list`.
        scale (int): scale of the export product.
        sdb_tiles (ee.ImageCollection): collection of subtidal bathymetry images corresponding
            to input tiles.
        name_suffix (str): unique identifier after tile statistics.
        task_list (List[ee.batch.Task]): list of tasks, adds tasks created to this list.
        overwrite (bool): whether to overwrite the current assets under the same `asset_path`.
        bucket (str): Bucket where the data is stored. Only used when sink = "cloud"
    
    returns:
        List[ee.batch.Task]: list of started tasks

    """
    if sink == "asset":
        user_name: str = ee.data.getAssetRoots()[0]["id"].split("/")[-1]
        asset_path_prefix: str = f"users/{user_name}/eo-bathymetry"
        ee.data.create_assets(asset_ids=[asset_path_prefix], asset_type="Folder", mk_parents=True)
    
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
        img_name: str = sub(r"\.\d+", "", f"z{zoom}_x{tx}_y{ty}_t") + name_suffix
        # Export image
        if sink == "asset":  # Replace with case / switch in python 3.10
            task: Optional[ee.batch.Task] = tile_to_asset(
                image=img,
                tile=temp_tile,
                export_scale=export_scale,
                asset_path_prefix=asset_path_prefix,
                asset_name=img_name,
                overwrite=overwrite
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
                overwrite=overwrite
            )
        else:
            raise ArgumentError("unrecognized data sink: {sink}")
        task_list.append(task)
    return task_list

def export_tiles_to_assets(
    sink: str,
    geometry: ee.Geometry,
    zoom: int,
    start: str,
    stop: str,
    step_months: int = 3,
    window_years: int = 2,
    overwrite: bool = False,
    bucket: Optional[str] = None
) -> None:
    """
    From a geometry, creates tiles of input zoom level, calculates subtidal bathymetry in those
    tiles, and exports those tiles.

    args:
        sink (str): type of data sink to export to. Viable options are: "asset" and "cloud".
        geometry (ee.Geometry): geometry of the area of interest.
        zoom (int): zoom level of the to-be-exported tiles.
        start (ee.String): start date in YYYY-MM-dd format.
        stop (ee.String): stop date in YYYY-MM-dd format.
        step_months (int): steps with which to roll the window over which the subtidal bathymetry
            is calculated.
        windows_years (int): number of years over which the subtidal bathymetry is calculated.
    """
    
    def create_year_window(year: ee.Number, month: ee.Number) -> ee.Dictionary:
        t: ee.Date = ee.Date.fromYMD(year, month, 1)
        d_format: str = "YYYY-MM-dd"
        return ee.Dictionary({
            "start": t.format(d_format),
            "stop": t.advance(window_years, 'year').format(d_format)
            })
        
    dates: ee.List = ee.List.sequence(parse(start).year, parse(stop).year).map(
        lambda year: ee.List.sequence(1, 12, step_months).map(partial(create_year_window, year))
    ).flatten()
    
    # Get tiles
    tiles: ee.FeatureCollection = tiler.get_tiles_for_geometry(geometry, ee.Number(zoom))

    scale: float = tiler.zoom_to_scale(zoom).getInfo()
    task_list: List[ee.batch.Task] = []
    num_tiles: int = tiles.size().getInfo()
    tile_list: ee.List = tiles.toList(num_tiles)

    for date in dates.getInfo():
        sdb_tiles: ee.ImageCollection = tiles.map(
            lambda tile: get_tile_bathymetry(
                tile=tile,
                start=ee.String(date["start"]),
                stop=ee.String(date["stop"])
            )
        )

        # Now export tiles
        export_sdb_tiles(
            sink=sink,
            tile_list=tile_list,
            num_tiles=num_tiles,
            export_scale=scale,
            sdb_tiles=sdb_tiles,
            name_suffix=f"{date['start']}_{date['stop']}",
            task_list=task_list,
            overwrite=overwrite,
            bucket=bucket
        )

