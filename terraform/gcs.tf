data "google_storage_project_service_account" "gcs_account" {
}

resource "google_storage_bucket" "budget_data_bucket" {
  name                     = var.budget_bucket
  location                 = var.location
  project                  = var.project_id
  public_access_prevention = "enforced"
}

resource "google_storage_bucket_iam_member" "bucket_reader" {
  bucket = google_storage_bucket.budget_data_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  depends_on = [google_storage_bucket.budget_data_bucket]
}