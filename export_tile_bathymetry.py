from functools import partial
from typing import Any, Dict, List
from re import sub

from dateutil.parser import parse
import ee
from eepackages.applications.bathymetry import Bathymetry
from eepackages import tiler

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

def export_sdb_tiles(
    tile_list: ee.List,
    num_tiles: int,
    scale: int,
    sdb_tiles: ee.ImageCollection,
    asset_path: str,
    name_suffix: str,
    task_list: List[ee.batch.Task],
    overwrite: bool
) -> List[ee.batch.Task]:
    """
    Export list of tiled images containing subtidal bathymetry. Fires off the tasks and adds to the list of tasks.
    based on: https://github.com/gee-community/gee_tools/blob/master/geetools/batch/imagecollection.py#L166

    args:
        tile_list (ee.List): list of tile features.
        num_tiles (int): number of tiles in `tile_list`.
        scale (int): scale of the export product.
        sdb_tiles (ee.ImageCollection): collection of subtidal bathymetry images corresponding
            to input tiles.
        asset_path (str): path to asset location.
        name_suffix (str): unique identifier after tile statistics.
        task_list (List[ee.batch.Task]): list of tasks, adds tasks created to this list.
        overwrite (bool): whether to overwrite the current assets under the same `asset_path`.
    
    returns:
        List[ee.batch.Task]: list of started tasks

    """
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
        # Export image
        img_name: str = sub(r"\.\d+", "", f"z{zoom}_x{tx}_y{ty}_t") + name_suffix
        asset_id: str = f"{asset_path}/{img_name}"
        asset: Dict[str, Any] = ee.data.getInfo(asset_id)
        if asset and overwrite:
            ee.data.deleteAsset(asset_id)
        elif asset:
            raise RuntimeError(f"asset {asset} already exists")
        task: ee.batch.Task = ee.batch.Export.image.toAsset(
            img,
            assetId=asset_id,
            description=img_name,
            region=temp_tile.geometry(),
            scale=scale
        )
        task.start()
        print(f"exporting {img_name} to {asset_id}")
        task_list.append(task)
    return task_list

def export_tiles_to_assets(
    asset_path: str,
    geometry: ee.Geometry,
    zoom: int,
    start: str,
    stop: str,
    step_months: int = 3,
    window_years: int = 2,
    overwrite: bool = False
) -> None:
    """
    From a geometry, creates tiles of input zoom level, calculates subtidal bathymetry in those
    tiles, and exports those tiles.

    args:
        asset_path (str): path to asset location.
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
            tile_list=tile_list,
            num_tiles=num_tiles,
            scale=scale,
            sdb_tiles=sdb_tiles,
            asset_path=asset_path,
            name_suffix=f"{date['start']}_{date['stop']}",
            task_list=task_list,
            overwrite=overwrite
        )
