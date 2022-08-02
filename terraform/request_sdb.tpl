{
    "geometry": {
        "type": "Polygon",
        "coordinates": [
${jsonencode(coordinates)}
        ]
    },
    "zoom": ${zoom},
    "export_zoom": ${export_zoom},
    "step_months": ${step_months},
    "window_years": ${window_years},
    "sink": {
        "type": "asset",
        "asset_path": "${asset_path}"
    }
}