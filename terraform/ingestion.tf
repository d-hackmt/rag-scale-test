# --- AUTO-INGESTION (EVENTARC TRIGGER) ---

# 1. The Ingestion Service (Receives the trigger)
resource "google_cloud_run_v2_service" "ingestion" {
  name     = "${var.app_name}-ingestion"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY" # Only Eventarc can talk to this

  template {
    service_account = google_service_account.ingestion_sa.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app_name}-repo/ingestion:latest"
      
      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
      }

      env {
        name  = "QDRANT_CLUSTER_ENDPOINT"
        value = var.qdrant_url
      }
      env {
        name  = "QDRANT_API_KEY"
        value = var.qdrant_api_key
      }
      env {
        name  = "DB_CONNECTION_NAME"
        value = google_sql_database_instance.postgres.connection_name
      }
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_RAW_BUCKET"
        value = google_storage_bucket.raw_data.name
      }
      env {
        name  = "GCP_PROCESSED_BUCKET"
        value = google_storage_bucket.processed_data.name
      }
    }
  }
}

# 2. Eventarc Trigger (Watches GCS)
resource "google_eventarc_trigger" "gcs_trigger" {
  name     = "rag-gcs-trigger"
  location = var.region
  
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }

  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.raw_data.name
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.ingestion.name
      region  = var.region
    }
  }

  service_account = google_service_account.ingestion_sa.email

  depends_on = [
    google_project_iam_member.ingestion_roles
  ]
}
