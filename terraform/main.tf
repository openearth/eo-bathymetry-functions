resource "google_service_account" "service_account" {
  account_id   = var.service_account_name
  display_name = "EO-Bathymetry service account."
}

resource "google_service_account_key" "service_account" {
  service_account_id = google_service_account.service_account.name
  public_key_type    = "TYPE_X509_PEM_FILE"
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
    command = "./zip_source.sh dist dist.zip"
  }
}

resource "google_storage_bucket_object" "archive" {
  name   = "${var.cloudfunction_entrypoint}.zip"
  bucket = google_storage_bucket.bathymetry_data.name
  source = "../dist/dist.zip"
  depends_on = [null_resource.create_zip_archive]
}

# # Below is commented as using secrets is still in beta
# resource "google_cloudfunctions_function" "function" {
#   name        = var.cloudfunction_name
#   description = "Exports bathymetry on a tile bases based on given region and time."
#   runtime     = "python39"

#   available_memory_mb   = var.function_memory
#   entry_point           = var.cloudfunction_entrypoint
#   region                = lower(var.region)
#   service_account_email = google_service_account.service_account.email
#   source_archive_bucket = google_storage_bucket.bathymetry_data.name
#   source_archive_object = google_storage_bucket_object.archive.name
#   timeout               = 540
#   trigger_http          = true

#   labels = var.labels
# }

resource "null_resource" "deploy_cloud_function" {
  # Create zip file containing python file that needs to be uploaded
  triggers = {
    python_zip = fileexists("../dist/dist.zip") ? filesha256("../dist/dist.zip") : random_id.this.id
  }

  provisioner "local-exec" {
    command = <<EOT
    gcloud beta functions deploy \
      ${var.cloudfunction_name} \
      --region=${lower(var.region)} \
      --entry-point=${var.cloudfunction_entrypoint} \
      --runtime=python39 \
      --memory=${var.function_memory}MB \
      --service-account=${google_service_account.service_account.email} \
      --source=gs://${google_storage_bucket.bathymetry_data.name}/${google_storage_bucket_object.archive.output_name} \
      --timeout=540 \
      --trigger-http \
      --set-env-vars="SA_EMAIL=${google_service_account.service_account.email}","SA_KEY_PATH=${var.service_account_key_path}" \
      --set-secrets="${var.service_account_key_path}=${google_secret_manager_secret.private_key.name}:${element(split("/", google_secret_manager_secret_version.private_key.name), length(split("/", google_secret_manager_secret_version.private_key.name))-1)}" \
      --allow-unauthenticated
    EOT
  }
}

resource "google_cloud_scheduler_job" "query_bathymetry_geo" {
  for_each = var.job_configs
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
      "${path.module}/request.tpl",
      merge(each.value, {bucket=var.bucket_name})
    ))
    headers     = {"Content-Type" = "application/json"}
  }

  depends_on = [null_resource.deploy_cloud_function]
}
