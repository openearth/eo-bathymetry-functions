from os import environ
from typing import Any, Dict

import ee
from flask import Request, Response
from geojson import loads
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from export_tile_bathymetry import export_tiles

credentials: ee.ServiceAccountCredentials = ee.ServiceAccountCredentials(environ.get("SA_EMAIL"), environ.get("SA_KEY_PATH"))
ee.Initialize(credentials=credentials)

PROJECT = environ.get("PROJECT")

# Create json schema to verify
schema: Dict[str, Any] = {
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
                }
            },
            "required": ["type"]
        }
    },
    "required": ["geometry", "start", "stop", "sink"]
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
            start: date string as YYYY-MM-dd, where the analysis starts.  TODO: can be just start_year?
            stop: date string as YYYY-MM-dd, where the analysis stops.  TODO: can just be stop_year?
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # Setup logging in cloud function
    global_log_fields: Dict[str, str] = {}
    trace_header: str = request.headers.get("X-Cloud-Trace-Context")
    if trace_header and PROJECT:
        trace = trace_header.split("/")
        global_log_fields["logging.googleapis.com/trace"] = f"projects/{PROJECT}/traces/{trace[0]}"

    json_body: Dict[any, str] = request.get_json()
    try:
        validate(instance=json_body, schema=schema)
    except (ValidationError) as e:
        return Response(e.message, status=400)

    geometry: Dict[str, Any] = ee.Geometry(loads(str(json_body["geometry"]).replace("'", "\"")))
    start: str = json_body["start"]
    stop: str = json_body["stop"]
    sink: str = json_body["sink"]["type"]
    bucket: str = json_body["sink"].get("bucket")
    
    export_tiles(
        sink=sink,
        geometry=geometry,
        zoom=10,
        start=start,
        stop=stop,
        bucket=bucket,
        global_log_fields=global_log_fields
    )

    return Response(status=200)