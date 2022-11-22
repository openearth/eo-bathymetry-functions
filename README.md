[![PyPi version](https://badgen.net/pypi/v/eo_bathymetry_functions/)](https://pypi.com/project/eo_bathymetry_functions)
[![CI](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/ci.yaml/badge.svg?branch=main&event=push)](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/ci.yaml)
[![CD](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/cd.yaml/badge.svg?branch=main&event=push)](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/cd.yaml)

# eo-bathymetry-functions
Automation of satellite-derived bathymetry generation with GSC Cloud Functions.

This repository contains code to create and export Satellite Derived Bathymetry images using
Google Earth Engine. The code consists of two Google Cloud Functions: one to create images and
export images to an `ImageCollection` in earthengine and one to export that `ImageCollection` as
tiles to cloud storage.
Python cloud functions in Cloud Functions are based on Flask APIs.

The infrastructure code (terraform) deploys all the infrastructure needed on google cloud. This
includes some google cloud buckets, access management, some objects in the bucket and the cloud
functions themselves, along with schedulers to query the functions.

## Terraform
This contains terraform code to set-up google cloud platform resources that are used in this
project. The state is stored in a cloud bucket that needs to be created manually. 

To obtain credentials to use for local development, use:
```gcloud auth application-default login --project bathymetry```

You need to enable the service account with google earth engine
[here](https://developers.google.com/earth-engine/guides/service_account).
You also need an app engine application for using the cloud scheduler.

When developing, use `make get_tf_key` to get your service account setup. Then you can 
`terraform plan -var-file workspaces/default.tfvars` in the terraform folder.

## Local Development
Install docker, pack cli, terraform, install gcloud and login to the bathymetry project as
described in the [terraform](#terraform) section. 2 Cloud Functions are used.
To test calculating and exporting bathymetry, use: `make local_deploy_sdb`.
To test exporting the hillshaded tiles, use: `make local_deploy_rgb`.
These commands start a docker image in the terminal, which exposes the cloud function on port 8080.

## Deployment
`make deploy` runs terraform and deploys to cloud functions.

## Adding schedulers
When adding a scheduler, add to the `job_configs` terraform variable in
`./terraform/workspaces/defaults.tfvars`, where the key is the name of the scheduler.

## Limitations

Due to the current implementation, this api needs to wait a few times on the earthengine api.
CloudFunctions times out at max 10 minutes. To create many tiles in one go (>100), please query
this api multiple times with different parameters.

## Example queries to the API

Query a small area and store the result in an asset.
```json
{
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [
                    4.726555204480136,
                    52.79894952106581
                ],
                [
                    5.382988309948886,
                    53.2615577684405
                ],
                [
                    5.226433134167636,
                    53.48931215536743
                ],
                [
                    4.770500516980136,
                    53.41898585234949
                ],
                [
                    4.270622587292636,
                    52.91018589685636
                ],
                [
                    4.726555204480136,
                    52.79894952106581
                ]
            ]
        ]
    },
    "zoom": 9,
    "export_zoom": 13,
    "overwrite": false,
    "start": "2015-01-01",
    "stop": "2017-01-01",
    "sink": {
        "type": "asset",
        "asset_path": "projects/deltares-rws/eo-bathymetry/test-collection"
    }
}
```

Use the previously created asset to store these images as tiles in cloud storage.
```json
{
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [
                    4.726555204480136,
                    52.79894952106581
                ],
                [
                    5.382988309948886,
                    53.2615577684405
                ],
                [
                    5.226433134167636,
                    53.48931215536743
                ],
                [
                    4.770500516980136,
                    53.41898585234949
                ],
                [
                    4.270622587292636,
                    52.91018589685636
                ],
                [
                    4.726555204480136,
                    52.79894952106581
                ]
            ]
        ]
    },
    "bucket": "eo-bathymetry-automation",
    "min_zoom": 8,
    "max_zoom": 10,
    "image_collection": "projects/deltares-rws/eo-bathymetry/test-collection"
}
```

## TODO
- Client side encryption: We can encrypt the terraform state at client side to enhance security.
    when secrets are used in the `variables.tf`.
