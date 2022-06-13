output sa_email {
  value       = google_service_account.service_account.email
  sensitive   = false
  description = "service account email"
}

output sa_key_path {
  value       = "${var.service_account_key_path}${var.service_account_key_subpath}"
  sensitive   = false
  description = "path on the docker image where the service account key is located"
}

