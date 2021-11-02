# eo-bathymetry-functions
Automation of satellite-derived bathymetry generation with GSC Cloud Functions

## Terraform
This contains terraform code to set-up google cloud platform resources that are used in this
project. The state is stored in a cloud bucket that needs to be created manually. 

To obtain credentials to use for local development, use:
```gcloud auth application-default login --project bathymetry```

You need to enable the service account with google earth engine
[here](https://developers.google.com/earth-engine/guides/service_account).

To deploy, run `terraform apply` or `make deploy`

## Local Development
Install docker, pack cli, terraform, install gcloud and login to the bathymetry project as
described in the [terraform](#terraform) section. Then run `make deploy-local`. This will start a
docker image in the terminal, which exposes the cloud function on port 8080.

### TODO
- Client side encryption: We can encrypt the terraform state at client side to enhance security.
    when secrets are used in the `variables.tf`.
- Scheduling: We need to schedule the cloud function using the cloud scheduler. We also want to
    easily add some queries to the scheduler.