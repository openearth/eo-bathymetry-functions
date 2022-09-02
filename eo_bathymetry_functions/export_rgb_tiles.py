from datetime import datetime
from dateutil.parser import parse
from json import dumps
from typing import Any, Dict, List, Optional

import ee

from eepackages.utils import hillshadeRGB
from eepackages.tiler import zoom_to_scale


def hillshade_sdb(image: ee.Image) -> ee.Image:
    """
    RGB hillshading specifically for the SDB product

    Args:
        image (ee.Image) earthengine image to be hillshaded
    
    Returns:
        (ee.Image) hillshaded image
    """
    depth: ee.Image = ee.Image(1).subtract(image.select([0, 1, 2]).rgbToHsv().select("value")).pow(2)
    weight: float = 0.6
    exaggeration: int = 2000
    azimuth: int = 315
    zenith: int = 35
    return hillshadeRGB(
        image=image, elevation=depth, weight=weight, height_multiplier=exaggeration,
        azimuth=azimuth, zenith=zenith).visualize()

def render_subtidal(
    ic: ee.ImageCollection,
    water_band: str = "water",
    water_min: float = -2.,
    water_max: float = 5.
) -> ee.Image:
    """
    renders subtidal images using hillshading and specific styiling options

    Args:
        ic (ee.ImageCollection): collection containing subtidal images
        water_band (str): band in the image that contains the water proxy
        water_min (float): minimum value for water band that gets scaled to 0
        water_max (float): maximum value for water band that gets scaled to 1
    
    Returns:
        (ee.Image) styled image from the ImageCollection
    """

    def styling(i: ee.Image) -> ee.Image:
        water: ee.Image = i.select(water_band).unitScale(water_min, water_max)

        return i.visualize() \
            .blend(hillshade_sdb(i.select([0, 1, 2]).unitScale(0, 2)).updateMask(water)) \
            .blend(water.mask(water).visualize(palette=["eff3ff","bdd7e7","6baed6","3182bd","08519c"], opacity=0.35)) \
            .copyProperties(i, ["system:time_start"]) \
            .copyProperties(i)
    return ic.map(styling).mosaic()

def export_timestep(
    timestep: str,
    ic: ee.ImageCollection,
    min_zoom: int,
    max_zoom: int,
    geometry: ee.Geometry,
    bucket: str,
    bucket_prefix: str,
    global_log_fields: Dict[str, str]
) -> List[ee.batch.Task]:
    # filter date is left-inclusive
    t0: ee.Date = ee.Date(timestep)
    t1: ee.Date = t0.advance(1, "day")
    ic = ic.filterDate(t0, t1)

    bucket_path: str = f"{bucket_prefix}/{timestep}"
    scale: float = zoom_to_scale(max_zoom)

    image: ee.Image = render_subtidal(ic) # .reproject('EPSG:3857')  # .reproject(
        # ee.Projection('EPSG:3857').atScale(zoom_to_scale(max_zoom)))
    task: ee.batch.Task = ee.batch.Export.map.toCloudStorage(
        image,
        description=f"sdb-3d-rws-{timestep}-z{max_zoom}",
        bucket=bucket,
        fileFormat="png",
        path=bucket_path,
        minZoom=min_zoom,
        maxZoom=max_zoom,
        region=geometry.bounds(scale),
        skipEmptyTiles=True,
        writePublicTiles=False  # Not bucket owner
    )
    task.start()

    print(dumps({
        "severity": "NOTICE",
        "message": f"exporting tiles to bucket {bucket}/{bucket_path}, taskid: {task.id}",
        **global_log_fields
    }))

def export_rgb_tiles(
    geometry: ee.Geometry,
    min_zoom: int,
    max_zoom: int,
    bucket: str,
    bucket_prefix: Optional[str],
    image_collection: str,
    start: Optional[str] = None,
    stop: Optional[str] = None,
    global_log_fields: Optional[Dict[str, Any]] = None
):
    """
    Args:
        geometry (ee.Geometry): geometry of the area of interest.
        min_zoom (int): tile minimum zoom level.
        max_zoom (int): tile maxumum zoom level.
        bucket (str): gcp bucket name.
        bucket_prefix (str): gcp bucket prefix
        image_collection (str): ImageCollection from where to import the bathymetry data.
        start (str): date string as YYYY-MM-dd, where the export starts.
        stop (str): date string as YYYY-MM-dd, where the export stops.
        global_log_fields (Optional(Dict)): log fields for the entire cloud function.
    Returns:

    """
    if not bucket_prefix:
        bucket_prefix = "sdb-tiles"
    if not start:
        start: datetime = parse(ee.Date(
            ee.ImageCollection(image_collection).aggregate_max("system:time_start")
        ).format("YYYY-MM-dd").getInfo())
    if not stop:
        now: datetime = datetime.now()
        stop: datetime = datetime(year=now.year, month=now.month, day=1)
    if start > stop:
        raise RuntimeError("Stop and Start too close")
    ic: ee.ImageCollection = ee.ImageCollection(image_collection) \
        .filterDate(start, stop) \
        .filterBounds(geometry)
    times: ee.List = ee.List(ic.aggregate_array('system:time_start'))

    times = times.map(lambda t: ee.Date(t).format('YYYY-MM-dd'))
    times = ee.List(times).distinct()
    for t in times.getInfo():
        export_timestep(
            timestep=t,
            ic=ic,
            min_zoom=min_zoom,
            max_zoom=max_zoom,
            geometry=geometry,
            bucket=bucket,
            bucket_prefix=bucket_prefix,
            global_log_fields=global_log_fields
        )
