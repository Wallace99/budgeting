resource "google_bigquery_dataset" "budgets_dataset" {
  dataset_id    = var.bq_dataset
  friendly_name = var.bq_dataset
  description   = "Budgeting data"
  location      = var.location
}


resource "google_bigquery_table" "budget_external_table" {
  dataset_id = google_bigquery_dataset.budgets_dataset.dataset_id
  table_id   = var.bq_table
  deletion_protection=false

  external_data_configuration {
    autodetect    = false
    source_format = "CSV"

    csv_options {
      skip_leading_rows = 1
      quote             = ""
      field_delimiter   = ","
    }

    source_uris = [
      "gs://${google_storage_bucket.budget_data_bucket.name}${var.budget_files_path}/*.csv"
    ]

    schema = <<EOF
      [
        {
          "name": "Date",
          "type": "DATE",
          "mode": "REQUIRED"
        },
        {
          "name": "Payee",
          "type": "STRING",
          "mode": "REQUIRED"
        },
        {
          "name": "Amount",
          "type": "FLOAT",
          "mode": "REQUIRED"
        },
        {
          "name": "Category",
          "type": "STRING",
          "mode": "REQUIRED"
        },
        {
          "name": "Particulars",
          "type": "STRING",
          "mode": "NULLABLE"
        },
        {
          "name": "Code",
          "type": "STRING",
          "mode": "NULLABLE"
        },
        {
          "name": "Reference",
          "type": "STRING",
          "mode": "NULLABLE"
        }
      ]
      EOF
  }
}