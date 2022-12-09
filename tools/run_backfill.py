import requests
from time import sleep

import pandas as pd
from retry.api import retry_call

url_sdb = "https://europe-west1-bathymetry.cloudfunctions.net/generate-bathymetry"
url_rgb = "https://europe-west1-bathymetry.cloudfunctions.net/generate-rgb-tiles"

time_start = "2013-01-01"
start_time_end = "2020-10-01"

dr = pd.date_range(time_start, start_time_end, freq="3MS")

time_bands = map(lambda d: (d.strftime("%Y-%m-%d"), (d + pd.DateOffset(years=2)).strftime("%Y-%m-%d")), dr)

geometry = {
    "type": "Polygon",
    "coordinates": [
        [
            [
                2.1379114173288514,
                51.293128274491586
            ],
            [
                2.434577524665388,
                50.920604754698104
            ],
            [
                3.4893648519040497,
                51.279391915875294
            ],
            [
                4.390334104842521,
                51.23813955644665
            ],
            [
                4.588103498320728,
                51.791975126338585
            ],
            [
                4.247490876553768,
                51.988625950681566
            ],
            [
                4.577112318328558,
                52.26518569517875
            ],
            [
                5.708821537267085,
                52.21136023592507
            ],
            [
                6.071406826426948,
                52.64015877655301
            ],
            [
                5.554993523607437,
                53.011941826417356
            ],
            [
                5.664867560921258,
                53.242693789891696
            ],
            [
                6.455968041721454,
                53.308396205716384
            ],
            [
                6.96139337053084,
                53.150542436017325
            ],
            [
                7.433856177115076,
                53.20322469622837
            ],
            [
                7.258056716197917,
                53.49836041191256
            ],
            [
                7.807433270201252,
                53.64190547111388
            ],
            [
                7.851382131427519,
                53.36744056524093
            ],
            [
                8.246932075595723,
                53.28212603987968
            ],
            [
                8.49964597768004,
                53.45258254510429
            ],
            [
                8.664460539456957,
                53.68747514808856
            ],
            [
                9.224824499059359,
                53.70048477855259
            ],
            [
                9.433589198160542,
                53.85630714886521
            ],
            [
                9.005076898848566,
                54.01800983912456
            ],
            [
                9.027054533151027,
                54.288259107842684
            ],
            [
                8.928170962953667,
                54.76647039361107
            ],
            [
                8.730397048304514,
                55.050715099021765
            ],
            [
                8.609537217180126,
                55.495118852064124
            ],
            [
                8.499663415186113,
                55.78657274380671
            ],
            [
                8.444935713313976,
                56.13358302289527
            ],
            [
                7.790672344250559,
                56.114654415229566
            ],
            [
                7.801747861258406,
                54.44588196627105
            ],
            [
                8.042203318168877,
                53.944119456233665
            ],
            [
                4.594031111232071,
                53.51319216872026
            ],
            [
                3.8075274264251737,
                52.25509342522693
            ],
            [
                3.304397467015563,
                51.531693064795505
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
        "asset_path": "projects/deltares-rws/eo-bathymetry/subtidal-nl"
    }
}

for t_start, t_end in time_bands:
    body_sdb["start"] = t_start
    body_sdb["stop"] = t_end
    res = retry_call(
        requests.post,
        fargs=(url_sdb,),
        fkwargs={"json": body_sdb, "timeout": 600},
        exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        jitter=(5,10)
    )
    sleep(60)
    print(res.content)

body_rgb = {
    "geometry": geometry,
    "bucket": "eo-bathymetry",
    "min_zoom": 0,
    "max_zoom": 13,
    "image_collection": "projects/deltares-rws/eo-bathymetry/subtidal-nl"
}

body_rgb["start"] = time_start
# res = retry_call(
#     requests.post,
#     fargs=(url_rgb,),
#     fkwargs={"json": body_rgb, "timeout": 600},
#     exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError),
#     jitter=(5,10),
# )
# print(res.content)
