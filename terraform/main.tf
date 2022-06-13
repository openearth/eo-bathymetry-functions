resource "google_service_account" "service_account" {
  account_id   = var.service_account_name
  display_name = "EO-Bathymetry service account."
}

resource "google_service_account_key" "service_account" {
  service_account_id = google_service_account.service_account.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_project_iam_member" "earthengine_writer" {
  project = var.project
  role    = "roles/earthengine.writer"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "service_user" {
  project = var.project
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_secret_manager_secret" "private_key" {
  secret_id = "eo-bathymetry-sa-key"

  replication {
    automatic = true
  }

  labels = var.labels
}

resource "google_secret_manager_secret_version" "private_key" {
  secret = google_secret_manager_secret.private_key.id
  secret_data = base64decode(google_service_account_key.service_account.private_key)
}

resource "google_secret_manager_secret_iam_member" "service_account" {
  project = var.project
  secret_id = google_secret_manager_secret.private_key.id
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.service_account.email}"
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
  mode            = "additive"

  bindings = {
    "roles/storage.objectAdmin" = [
      "serviceAccount:${google_service_account.service_account.email}"
    ]
  }
  # conditional_bindings none as we link the service account directly to the bucket
}

resource "random_id" "this" {
  # create random trigger if dist changes
  keepers = {
    always_run = "${timestamp()}"
  }
  byte_length = 10
}

resource "null_resource" "create_zip_archive" {
  # Create zip file containing python file that needs to be uploaded
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    command = "./zip_source.sh gcloud_dist dist${random_id.this.dec}.zip"
  }
}

resource "google_storage_bucket_object" "archive" {
  name   = "sdb.zip"
  bucket = google_storage_bucket.bathymetry_data.name
  source = "../gcloud_dist/dist${random_id.this.dec}.zip"
  depends_on = [null_resource.create_zip_archive]
}

# Below is commented as using secrets is still in beta
resource "google_cloudfunctions_function" "function" {
  for_each    = var.cloudfunction_entrypoints
  name        = each.key
  description = "Exports bathymetry on a tile bases based on given region and time."
  runtime     = "python39"

  available_memory_mb   = var.function_memory
  entry_point           = each.value
  region                = lower(var.region)
  service_account_email = google_service_account.service_account.email
  source_archive_bucket = google_storage_bucket.bathymetry_data.name
  source_archive_object = google_storage_bucket_object.archive.name
  timeout               = 540
  trigger_http          = true

  environment_variables = {
    "SA_EMAIL" = google_service_account.service_account.email,
    "SA_KEY_PATH" = "${var.service_account_key_path}${var.service_account_key_subpath}"
  }

  secret_volumes {
    mount_path = var.service_account_key_path
    secret = element(
      split("/", google_secret_manager_secret.private_key.name),
      length(split("/", google_secret_manager_secret.private_key.name))-1
    )
    
    versions {
      path = var.service_account_key_subpath
      version = element(
        split("/", google_secret_manager_secret_version.private_key.name),
        length(split("/", google_secret_manager_secret_version.private_key.name))-1
      )
    }
  }

  labels = var.labels
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  for_each       = var.cloudfunction_entrypoints
  project        = google_cloudfunctions_function.function[each.key].project
  region         = google_cloudfunctions_function.function[each.key].region
  cloud_function = google_cloudfunctions_function.function[each.key].name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

resource "google_cloud_scheduler_job" "query_bathymetry_geo" {
  for_each = var.sdb_job_configs
  name             = each.key
  description      = each.value["description"]
  schedule         = each.value["cron_schedule"]
  time_zone        = each.value["time_zone"]
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = each.value["http_method"]
    uri         = each.value["uri"]
    body        = base64encode(templatefile(
      "${path.module}/request_sdb.tpl",
      merge(each.value, {bucket=var.bucket_name})
    ))
    headers     = {"Content-Type" = "application/json"}
  }

  depends_on = [google_cloudfunctions_function.function]
}

resource "google_cloud_scheduler_job" "query_rgb_geo" {
  for_each = var.rgb_job_configs
  name             = each.key
  description      = each.value["description"]
  schedule         = each.value["cron_schedule"]
  time_zone        = each.value["time_zone"]
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = each.value["http_method"]
    uri         = each.value["uri"]
    body        = base64encode(templatefile(
      "${path.module}/request_rgb.tpl",
      merge(each.value, {bucket=var.bucket_name})
    ))
    headers     = {"Content-Type" = "application/json"}
  }

  depends_on = [google_cloudfunctions_function.function]
}