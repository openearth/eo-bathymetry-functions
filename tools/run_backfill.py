from copy import copy
import requests

import pandas as pd

url_sdb = "https://europe-west1-bathymetry.cloudfunctions.net/generate-bathymetry"
url_rgb = "https://europe-west1-bathymetry.cloudfunctions.net/generate-rgb-tiles"

time_start = "2015-01-01"
start_time_end = "2019-08-01"

dr = pd.date_range(time_start, start_time_end, freq="3YS")

time_bands = map(lambda d: (d.strftime("%Y-%m-%d"), (d + pd.DateOffset(years=1)).strftime("%Y-%m-%d")), dr)

geometry = {
    "type": "Polygon",
    "coordinates": [
        [
            [
                5.795880648281493,
                51.52322043928555
            ],
            [
                7.597638460781493,
                52.60383266102908
            ],
            [
                10.014630648281493,
                53.38409943602731
            ],
            [
                10.168439242031493,
                54.26597908534566
            ],
            [
                9.245587679531493,
                56.0604912541101
            ],
            [
                7.092267367031493,
                56.207423002919064
            ],
            [
                7.158185335781493,
                55.09168342821415
            ],
            [
                6.608868929531493,
                54.59827676009737
            ],
            [
                3.928204867031493,
                54.16319085617696
            ],
            [
                2.368146273281493,
                52.25550015782851
            ],
            [
                2.434064242031493,
                51.16637724261702
            ],
            [
                3.642560335781493,
                50.80675167573701
            ],
            [
                5.795880648281493,
                51.52322043928555
            ]
        ]
    ]
}

body_sdb = {
    "geometry": geometry,
    "zoom": 9,
    "export_zoom": 13,
    "sink": {
        "type": "asset",
        "asset_path": "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
    }
}

sdb_bodies = []

for t_start, t_end in time_bands:
    new_body = copy(body_sdb)
    new_body["start"] = t_start
    new_body["end"] = t_end
    sdb_bodies.append(new_body)

for body in sdb_bodies:
    res = requests.post(url_sdb, data=body)
    print(res.content)

body_rgb = {
    "geometry": geometry,
    "bucket": "eo-bathymetry",
    "min_zoom": 0,
    "max_zoom": 13,
    "image_collection": "projects/deltares-rws/eo-bathymetry/depth-uncalibrated"
}
