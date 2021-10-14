resource "google_service_account" "service_account" {
  account_id   = "eo-bathymetry-automation"
  display_name = "EO-Bathymetry service account."
}

resource "google_storage_bucket" "bathymetry_data" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
  labels = var.labels
}

module "storage_bucket-iam-bindings" {
  source          = "terraform-google-modules/iam/google//modules/storage_buckets_iam"
  storage_buckets = [google_storage_bucket.bathymetry_data.name]
  mode            = "authoritative"

  bindings = {
    "roles/storage.objectAdmin" = [
      "serviceAccount:${google_service_account.service_account.email}"
    ]
  }
  # conditional_bindings none as we link the service account directly to the bucket
}

# resource "google_service_account_key" "cloudfunction_key" {
#   service_account_id = google_service_account.service_account.name
#   public_key_type    = "TYPE_X509_PEM_FILE"
# }

resource "random_id" "this" {
  # create random trigger if file does not exist
  byte_length = 10
}

resource "null_resource" "create_zip_archive" {
  # Create zip file containing python file that needs to be uploaded
  triggers = {
    python_zip = fileexists("../dist/dist.zip") ? filesha256("../dist/dist.zip") : random_id.this.id
  }

  provisioner "local-exec" {
    command = "./zip_source.sh dist dist${random_id.this.dec}.zip"
  }
}

resource "google_storage_bucket_object" "archive" {
  name   = "${var.cloudfunction_entrypoint}.zip"
  bucket = google_storage_bucket.bathymetry_data.name
  source = "../dist/dist${random_id.this.dec}.zip"
  depends_on = [null_resource.create_zip_archive]
}

resource "google_cloudfunctions_function" "function" {
  name        = var.cloudfunction_name
  description = "Exports bathymetry on a tile bases based on given region and time."
  runtime     = "python39"

  available_memory_mb   = var.function_memory
  entry_point           = var.cloudfunction_entrypoint
  region                = lower(var.region)
  service_account_email = google_service_account.service_account.email
  source_archive_bucket = google_storage_bucket.bathymetry_data.name
  source_archive_object = google_storage_bucket_object.archive.name
  timeout               = 540
  trigger_http          = true

  labels = var.labels
}


# TODO
# resource "google_cloud_scheduler_job" {
    
# }