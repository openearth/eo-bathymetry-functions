{
    "geometry": {
        "type": "Polygon",
        "coordinates": [
${jsonencode(coordinates)}
        ]
    },
    "bucket": ${bucket},
    "max_zoom": ${max_zoom},
    "min_zoom": ${min_zoom},
    "image_collection": ${image_collection}
}