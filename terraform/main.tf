data "google_project" "project" {
  project_id = var.project_id
}

data "google_storage_project_service_account" "gcs_account" {
}

resource "google_cloud_run_v2_service" "budget" {
  name     = "budget-categorise"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    scaling {
      max_instance_count = 1
    }

    containers {
      image = "us-central1-docker.pkg.dev/rising-sector-360922/budget-artifact-registry/category-assigner:${var.image_tag}"

      env {
        name  = "project_id"
        value = var.project_id
      }

      env {
        name  = "bq_dataset"
        value = "budgeting"
      }

      env {
        name  = "bq_table"
        value = "budgeting"
      }
    }
  }
}

resource "google_storage_bucket" "budget_data_bucket" {
  name                     = "budget-data"
  location                 = "us-central1"
  project                  = var.project_id
  public_access_prevention = "enforced"
}

# Create a GCS trigger
resource "google_eventarc_trigger" "trigger_bucket" {
  name     = "trigger-bucket"
  location = google_cloud_run_v2_service.budget.location

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }

  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.budget_data_bucket.name
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.budget.name
      region  = google_cloud_run_v2_service.budget.location
      path    = "/"
    }
  }

  service_account = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"

  depends_on = [google_project_iam_member.gcs_pubsub_member]
}

resource "google_project_iam_member" "gcs_pubsub_member" {
  project = var.project_id
  member  = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
  role    = "roles/pubsub.publisher"
}