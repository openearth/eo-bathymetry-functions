variable bucket_name {
  type        = string
  default     = "eo-bathymetry-automation"
  description = "Bucket to storage automatically generated images."
}

variable region {
  type        = string
  default     = "EUROPE-WEST1"  # Netherlands
  description = "Location of bucket"
}

variable service_account_name {
  type        = string
  default     = "eo-bathymetry-automation"
  description = "name of service account used for the cloud function"
}

variable service_account_key_path {
  type        = string
  default     = "/etc/secrets/eo-bathymetry-sa-key"
  description = <<EOT
    path where the private key of the service account is mounted in the
    cloudfunction image.
  EOT
}

variable service_account_key_subpath {
  type        = string
  default     = "/key.json"
  description = <<EOT
    subpath where the private key of the service account is mounted in the
    cloudfunction image. Has to start with a forward-slash.
  EOT
}

variable cloudfunction_entrypoints {
  type        = map(string)
  default     = {
    "generate-bathymetry" = "generate_bathymetry",
    "generate-rgb-tiles"  = "generate_rgb_tiles"

  }
  description = "map of the name of the cloud function plus the python names of their entrypoints."
}

variable function_memory {
  type        = number
  default     = 256
  description = "Cloud function memory in MB"
}

variable labels {
  type        = map(string)
  default     = {
      "project_name" = "eo-bathymetry",
      "unit" = "sdi"
  }
  description = "default set of labels applied to resources."
}

variable project {
  type        = string
  default     = "bathymetry"
  description = "project name"
}

variable job_configs {
  type        = map(
    object({
      description = string,
      cron_schedule = string,
      time_zone = string,
      http_method = string,
      uri = string,
      coordinates = list(tuple([number, number])),
      zoom = number,
      step_months = number,
      window_years = number,
    })
  )
  description = "configuration for the cron-based cloud scheduler jobs."
  default = {}
}