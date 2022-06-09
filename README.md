[![PyPi version](https://badgen.net/pypi/v/eo_bathymetry_functions/)](https://pypi.com/project/eo_bathymetry_functions)
[![CI](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/ci.yaml/badge.svg?branch=main&event=push)](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/ci.yaml)
[![CD](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/cd.yaml/badge.svg?branch=main&event=push)](https://github.com/openearth/eo-bathymetry-functions/actions/workflows/cd.yaml)

# eo-bathymetry-functions
Automation of satellite-derived bathymetry generation with GSC Cloud Functions

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
described in the [terraform](#terraform) section. Then run `make local-deploy`. This will start a
docker image in the terminal, which exposes the cloud function on port 8080.

## Deployment
`make deploy`

## Adding schedulers
When adding a scheduler, add to the `job_configs` terraform variable in
`./terraform/workspaces/defaults.tfvars`, where the key is the name of the scheduler.

### TODO
- Client side encryption: We can encrypt the terraform state at client side to enhance security.
    when secrets are used in the `variables.tf`.
