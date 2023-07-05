data "google_storage_project_service_account" "gcs_account" {
}

resource "google_storage_bucket" "budget_data_bucket" {
  name                     = var.budget_bucket
  location                 = var.location
  project                  = var.project_id
  public_access_prevention = "enforced"
}