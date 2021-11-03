{
    "geometry": {
        "type": "Polygon",
        "coordinates": [
${jsonencode(coordinates)}
        ]
    },
    "zoom": ${zoom},
    "step_months": ${step_months},
    "window_years": ${window_years},
    "sink": {
        "type": "cloud",
        "bucket": "${bucket}"
    }
}