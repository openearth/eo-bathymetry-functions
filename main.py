from os import environ
from typing import Any, Dict, Optional, Union

import ee
from flask import Request, Response
from geojson import loads
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from eo_bathymetry_functions.export_tile_bathymetry import export_tiles
from eo_bathymetry_functions.export_rgb_tiles import export_rgb_tiles
from eo_bathymetry_functions.utils import set_up_cf_logging

credentials: ee.ServiceAccountCredentials = ee.ServiceAccountCredentials(environ.get("SA_EMAIL"), environ.get("SA_KEY_PATH"))
ee.Initialize(credentials=credentials)

# Create json schema to verify
schema_generate_bathymetry: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "geometry": {
            "type": "object",
            "properties": {
                "type": {"enum": ["Polygon"]},
                "coordinates": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "items": {type: "number"},
                            "minItems": 2,
                            "maxItems": 2
                        }
                    }
                }
            },
            "required": ["coordinates"]
        },
        "zoom": {
            "type": "number"
        },
        "export_zoom": {
            "type": "number"
        },
        "start": {
            "type": "string",
            "pattern": "\d{4}-\d{2}-\d{2}"
        },
        "stop": {
            "type": "string",
            "pattern": "\d{4}-\d{2}-\d{2}"
        },
        "sink": {
            "type": "object",
            "properties": {
                "type": {
                    "enum": ["cloud", "asset"],
                },
                "bucket": {
                    "type": "string",
                    "pattern": "[\w\-]{3,62}|(?=.*\.)[\w\-\.]{3,222}"
                },
                "asset_path": {
                    "type": "string",
                    "pattern": "[\w\-]{3,62}|(?=.*\.)[\w\-\.]{3,222}"
                }
            },
            "required": ["type"]
        },
        "step_months": {
            "type": "number"
        },
        "window_years": {
            "type": "number"
        }
    },
    "required": ["geometry", "zoom", "sink"]
}

def generate_bathymetry(request: Request):
    """
    Http Cloud function for generating bathymetry.
    Args:
        request (flask.Request): the Request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
        Requires the following body:
            geometry: (Geo)JSON representation of the Geometry that will be used to calculate the
                subtidal bathymetry.
            zoom: earth engine zoom level for creating tiles.
            sink: json object describing the data sink. Can either be:
                {"type": "cloud", "bucket": "bucket_name"}
                or {"type": "asset", "asset_path": "path/to/asset"}
                asset path should point to ImageCollection or Folder, names of images are generated
                automatically based on tile and time
        
        optionally:
            start: date string as YYYY-MM-dd, where the analysis starts.
            stop: date string as YYYY-MM-dd, where the analysis stops.
            step_months: number of months to include in each timestep, defaults to 3.
            window_years: number of years to include in the analysis, defaults to 2.
            export_zoom: zoom level for export quality. Defaults to zoom. Used internally to
                determine the quality of the exported image. Larger zoom number result in more
                calculations, but higher resolution images.
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # Setup logging in cloud function
    global_log_fields: Dict[str, str] = set_up_cf_logging(request)

    json_body: Dict[any, str] = request.get_json()
    try:
        validate(instance=json_body, schema=schema_generate_bathymetry)
    except (ValidationError) as e:
        return Response(e.message, status=400)

    kwargs: Dict[str, Any] = {}

    kwargs["geometry"] = ee.Geometry(loads(str(json_body["geometry"]).replace("'", "\"")))
    kwargs["zoom"] = json_body["zoom"]
    kwargs["export_zoom"] = json_body.get("export_zoom")
    kwargs["start"] = json_body.get("start")
    kwargs["stop"] = json_body.get("stop")
    kwargs["sink"] = json_body["sink"]["type"]
    kwargs["bucket"] = json_body["sink"].get("bucket")
    kwargs["asset_path"] = json_body["sink"].get("asset_path")
    step_months_opt: Optional[Union[int, float]] = json_body.get("step_months")
    window_years_opt: Optional[Union[int, float]] = json_body.get("step_months")
    
    if step_months_opt:
        kwargs["step_months"] = int(step_months_opt)
    
    if window_years_opt:
        kwargs["window_years"] = int(window_years_opt)
        
    export_tiles(
        **kwargs,
        global_log_fields=global_log_fields
    )

    return Response(status=200)

schema_export_rgb_tiles: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "geometry": {
            "type": "object",
            "properties": {
                "type": {"enum": ["Polygon"]},
                "coordinates": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "items": {type: "number"},
                            "minItems": 2,
                            "maxItems": 2
                        }
                    }
                }
            },
            "required": ["coordinates"]
        },
        "max_zoom": {
            "type": "number"
        },
        "min_zoom": {
            "type": "number"
        },
        "start": {
            "type": "string",
            "pattern": "\d{4}-\d{2}-\d{2}"
        },
        "stop": {
            "type": "string",
            "pattern": "\d{4}-\d{2}-\d{2}"
        },
        "image_collection": {
            "type": "string"
            # TODO: validation here
        },
        "bucket": {
            "type": "string",
            "pattern": "[\w\-]{3,62}|(?=.*\.)[\w\-\.]{3,222}"
        }
    },
    "required": ["geometry", "min_zoom", "max_zoom", "bucket"]
}


def generate_rgb_tiles(request: Request):
    """
    Http Cloud function for generating RGB tiles from existing bathymetry.
    Args:
        request (flask.Request): the Request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
        Requires the following body:
            geometry: containing the erea of interest
            min_zoom: tile minimum zoom level
            max_zoom: tile maxumum zoom level
            bucket: gcp bucket name
        
        optionally:
            image_collection: image_collection to load from. Defaults to TODO
            start: date string as YYYY-MM-dd, where the analysis starts.
            stop: date string as YYYY-MM-dd, where the analysis stops.
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # Setup logging in cloud function
    global_log_fields: Dict[str, str] = set_up_cf_logging(request)

    json_body: Dict[any, str] = request.get_json()
    try:
        validate(instance=json_body, schema=schema_export_rgb_tiles)
    except (ValidationError) as e:
        return Response(e.message, status=400)

    kwargs: Dict[str, Any] = {}

    kwargs["geometry"] = ee.Geometry(loads(str(json_body["geometry"]).replace("'", "\"")))
    kwargs["min_zoom"] = json_body["min_zoom"]
    kwargs["max_zoom"] = json_body["max_zoom"]
    kwargs["bucket"] = json_body["bucket"]
    kwargs["start"] = json_body.get("start")
    kwargs["stop"] = json_body.get("stop")

    opt_image_collection: Optional[str] = json_body.get("image_collection")
    if opt_image_collection:
        kwargs["image_collection"] = opt_image_collection
        
    export_rgb_tiles(
        **kwargs,
        global_log_fields=global_log_fields
    )

    return Response(status=200)