variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "location" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "bq_table" {
  description = "Name of the BigQuery external table."
  type        = string
}

variable "bq_dataset" {
  description = "Name of the BigQuery dataset containing budgeting tables."
  type        = string
}

variable "image_tag" {
  description = "Cloud Run image tag"
  type        = string
}

variable "budget_bucket" {
  description = "Name of the bucket containing the budget files."
  type        = string
}

variable "budget_files_path" {
  description = "The path to where processed budget files are and picked up by a BigQuery external table. Starts with '/'."
  type        = string
}