# ☁️ Cloud Infrastructure (IaC)

We use **Infrastructure as Code (IaC)** via **Terraform** to ensure that our GCP environment is reproducible, secure, and documented.

---

## 🛠️ The Terraform Stack

### 1. Networking & Identity (IAM)
- **Service Accounts**: Each microservice has its own dedicated Service Account with "Least Privilege" permissions.
- **IAM Policies**: The Ingestion worker has permission to read from GCS, while the UI only has permission to call the Backend.

### 2. Managed Services
- **Artifact Registry**: A private Docker repository hosted in `us-central1` to store our images.
- **Cloud SQL**: A managed Postgres instance with `db-f1-micro` tier for cost-efficient production memory.
- **Secret Management**: (In progress) Moving from Environment Variables to GCP Secret Manager.

### 3. Eventarc (The Automation Engine)
This is the "Glue" of the system.
- **Source**: GCS Bucket (`object.v1.finalized` event).
- **Destination**: Ingestion Cloud Run Service.
- **Logic**: When a file is finished uploading, Eventarc captures the metadata and sends an HTTP POST request to the worker to start the ingestion.

---

## 🏗️ Managing the Infrastructure
- **Initialization**: `terraform init` (Sets up the state).
- **Deployment**: `terraform apply` (Builds the cloud).
- **Destruction**: `terraform destroy` (Cleans up the cloud to save costs).

> [!WARNING]
> Always verify the `terraform plan` before applying to avoid accidental deletion of data buckets or databases.
