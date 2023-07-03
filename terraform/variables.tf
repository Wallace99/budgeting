variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "image_tag" {
  description = "Cloud Run image tag"
  type = string
  default = "latest"
}