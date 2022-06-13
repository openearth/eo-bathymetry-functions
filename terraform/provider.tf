terraform {
  required_version = ">= 1.0.8"
  backend "gcs" {
    bucket = "eo-bathymetry-terraform-state"
    prefix = "eo-bathymetry-functions"

    # TODO: Client side encryption
  }
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 4.22.0"
    }
    null = {
      source = "hashicorp/null"
      version = "3.1.0"
    }
    random = {
      source = "hashicorp/random"
      version = "3.1.0"
    }
  }
}

provider "google" {
  project = var.project
  region = lower(var.region)
  credentials = "../gcloud_dist/terraform_sa_key.json"
}

provider "null" {}

provider "random" {}
