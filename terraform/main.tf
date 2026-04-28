# --- CORE INFRASTRUCTURE ---

# 1. Enable Required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com",
    "discoveryengine.googleapis.com",
    "pubsub.googleapis.com",
    "eventarc.googleapis.com"
  ])
  service = each.key
  disable_on_destroy = false
}

# 2. Service Account for Ingestion
resource "google_service_account" "ingestion_sa" {
  account_id   = "rag-ingestion-sa"
  display_name = "RAG Ingestion Service Account"
}

# Grant SA permission to read from bucket and write to logs
resource "google_project_iam_member" "ingestion_roles" {
  for_each = toset([
    "roles/storage.objectViewer",
    "roles/logging.logWriter",
    "roles/aiplatform.user"
  ])
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.ingestion_sa.email}"
}

# 2. Storage Buckets
resource "google_storage_bucket" "raw_data" {
  name     = "${var.project_id}-rag-raw"
  location = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "processed_data" {
  name     = "${var.project_id}-rag-processed"
  location = var.region
  uniform_bucket_level_access = true
}

# 3. Artifact Registry for Docker Images
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${var.app_name}-repo"
  description   = "Docker repository for RAG Microservices"
  format        = "DOCKER"
}
