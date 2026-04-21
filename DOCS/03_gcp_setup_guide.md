# GCP Configuration & Step-by-Step Setup

Follow these steps on the [Google Cloud Console](https://console.cloud.google.com) to prepare your environment for the target architecture.

## Step 1: Project & APIs
1.  **Create a New Project** (e.g., `scalable-rag-enterprise`).
2.  **Enable APIs**:
    - Vertex AI API
    - Cloud Storage API
    - Cloud Run API (or Kubernetes Engine API)
    - Cloud SQL Admin API
    - Compute Engine API

## Step 2: Service Account Setup
Create a service account specifically for the RAG system:
1.  Go to **IAM & Admin > Service Accounts**.
2.  Click **Create Service Account** (name: `rag-agent-svc`).
3.  **Assign Roles**:
    - `Vertex AI User`: To generate embeddings and chat.
    - `Storage Object Admin`: To read/write to GCS.
    - `Cloud SQL Client`: To connect to Postgres.
    - `Logging Admin`: To send logs to Cloud Logging.
4.  **Download Key**: Select the account -> Keys -> Add Key -> JSON. Save this locally (and add to `.gitignore`!).

## Step 3: Cloud Storage Bucket
1.  Go to **Cloud Storage > Buckets**.
2.  Create a bucket (e.g., `rag-enterprise-assets`).
3.  Create folders:
    - `/raw_docs/`: For original PDFs.
    - `/processed_chunks/`: For indexing metadata.
    - `/vector_indices/`: For any remaining flat-file indices.

## Step 4: Qdrant Setup (Vector DB)
**Option: GKE Deployment**
- Use the Qdrant [Helm Chart](https://qdrant.tech/documentation/guides/installation/) to deploy to GKE.
- Expose the service internally using a **Private Load Balancer**.

## Step 5: Environment Variables (.env)
Update your local and cloud `.env` with these new keys:
```env
PROJECT_ID="your-project-id"
LOCATION="us-central1"
BUCKET_NAME="rag-enterprise-assets"

# Qdrant Config
QDRANT_HOST="internal.qdrant.svc.cluster.local" # If on GKE
QDRANT_API_KEY="your-qdrant-key"

# Neo4j Config
NEO4J_URI="bolt://your-neo4j-instance"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-secure-password"
```

## Security Best Practices
- **Never** commit your Service Account JSON to GitHub.
- Use **Secret Manager** to store API keys for Neo4j and Qdrant.
- Use **Identity-Aware Proxy (IAP)** to protect your Streamlit UI.
