terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.69.1"
    }
  }
}

provider "google" {
  project = "rising-sector-360922"
  # Not sure why this is needed, something about my setup is meaning it's not picking up ADC automatically
  credentials = "/Users/wallaced/.config/gcloud/application_default_credentials.json"
}