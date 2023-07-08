data "google_project" "project" {
  project_id = var.project_id
}

resource "google_service_account" "cloud_run_sa" {
  account_id = "budget-service"
  project = var.project_id
}

resource "google_cloud_run_v2_service" "budget" {
  name     = "budget-categorise"
  location = var.location
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      max_instance_count = 1
    }

    containers {
      image = "${var.location}-docker.pkg.dev/${var.project_id}/budget-artifact-registry/category-assigner:${var.image_tag}"

      env {
        name  = "project_id"
        value = var.project_id
      }

      env {
        name  = "bq_dataset"
        value = var.bq_dataset
      }

      env {
        name  = "bq_table"
        value = var.bq_table
      }
    }
  }
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

  service_account = google_service_account.cloud_run_sa.email

  depends_on = [google_project_iam_member.gcs_pubsub_member]
}

resource "google_project_iam_member" "gcs_pubsub_member" {
  project = var.project_id
  member  = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
  role    = "roles/pubsub.publisher"
}

resource "google_project_iam_member" "event_receiver_member" {
  project = var.project_id
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  role = "roles/eventarc.eventReceiver"
}