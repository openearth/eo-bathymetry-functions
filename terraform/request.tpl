{
    "geometry": {
        "type": "Polygon",
        "coordinates": [
${jsonencode(coordinates)}
        ]
    },
    "zoom": ${zoom},
    "start": "${start}",
    "stop": "${stop}",
    "step_months": ${step_months},
    "window_years": ${window_years},
    "sink": {
        "type": "cloud",
        "bucket": "${bucket}"
    }
}