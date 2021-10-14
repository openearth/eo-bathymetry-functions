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

variable cloudfunction_name {
  type        = string
  default     = "export-tile-bathymetry"
  description = "name of the cloud function"
}

variable cloudfunction_entrypoint {
  type        = string
  default     = "generate_bathymetry"
  description = "name of the function that will function as the entrypoint"
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