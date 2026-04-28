# 🚀 GCP Production Setup

Your system is designed to run on a fully managed, serverless stack on Google Cloud Platform.

## 🛠️ Infrastructure Components
-   **Cloud Run**: Hosts the Backend, UI, and Ingestion services.
-   **Cloud SQL (Postgres)**: Managed database for agent memory.
-   **Artifact Registry**: Secure storage for Docker images.
-   **GCS Buckets**: Data storage for raw and processed documents.
-   **Eventarc**: The automated trigger system for ingestion.

## 🚢 Deployment Steps
1.  **Build**: `gcloud builds submit --config cloudbuild.yaml .`
2.  **Provision**: `cd terraform && terraform apply`
3.  **Verify**: Access the `ui_url` printed by Terraform.

## 🔐 Security Best Practices
-   **Secrets**: All API keys are passed securely via Terraform variables.
-   **Networking**: Services use internal communication where possible to reduce exposure.
-   **IAM**: Each service runs with a dedicated service account.
