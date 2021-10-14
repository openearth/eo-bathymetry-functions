# eo-bathymetry-functions
Automation of satellite-derived bathymetry generation with GSC Cloud Functions

## Terraform
This contains terraform code to set-up google cloud platform resources that are used in this
project. The state is stored in a cloud bucket that needs to be created manually. 

To obtain credentials to use for local development, use:
```gcloud auth application-default login --project bathymetry```

You need to enable the service account with google earth engine
[here](https://developers.google.com/earth-engine/guides/service_account).

### Automation TODO
- Client side encryption: We can encrypt the terraform state at client side to enhance security.
    when secrets are used in the `variables.tf`, this is a valuable tool.