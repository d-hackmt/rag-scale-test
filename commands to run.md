# 🗺️ The Enterprise RAG Playbook

This guide contains every command needed to manage, build, and deploy your Agentic RAG system.

---

## 💻 Phase 1: Local Development (Fast Logic Testing)
*Run these to test your code changes instantly without waiting for Docker.*

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Backend (Brain)**:
   ```bash
   # Starts the FastAPI server on port 8000
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start the UI (Face)**:
   ```bash
   # Starts Streamlit. It will automatically talk to the backend on localhost:8000
   streamlit run ui/app.py
   ```

---

## 📦 Phase 2: Local Docker (Environment Testing)
*Run these to ensure your containers and environment variables are working correctly.*

1. **Build and Start Everything**:
   ```bash
   # Orchestrates Backend, UI, and Local Postgres
   docker-compose up --build
   ```

2. **Clean Shutdown**:
   ```bash
   docker-compose down -v
   ```

---

## ☁️ Phase 3: Cloud Building (Google Cloud Build)
*Packages your code into professional, production-grade images.*

1. **Build All Services (Long build)**:
   ```bash
   # Builds Backend, UI, and Ingestion worker
   gcloud builds submit --config cloudbuild.yaml .
   ```

2. **Build Only Ingestion (Fast update)**:
   ```bash
   # Use this when you only change the document processing logic
   gcloud builds submit --config cloudbuild-ingestion.yaml .
   ```

---

## 🏗️ Phase 4: Infrastructure (Terraform)
*Provisions the Database, Storage, and Cloud Run services.*

1. **Initialize & Sync**:
   ```bash
   cd terraform
   /c/terraform/terraform.exe init
   ```

2. **The "Recovery" Imports (Run if resources already exist)**:
   ```bash
   # Import the Registry
   /c/terraform/terraform.exe import google_artifact_registry_repository.repo projects/dmtxpress/locations/us-central1/repositories/enterprise-rag-repo

   # Import the Database
   /c/terraform/terraform.exe import google_sql_database_instance.postgres projects/dmtxpress/instances/enterprise-rag-db
   ```

3. **Final Deployment**:
   ```bash
   # This will create/update all Cloud Run services and link them together
   /c/terraform/terraform.exe apply
   ```

---

## ⚙️ Phase 5: Production Operations
*How to actually use the system once it is live.*

1. **Ingest Documents**:
   - Simply upload a PDF to your Raw GCS bucket (find the name in the GCP Console).
   - The **Eventarc Trigger** will automatically wake up the Ingestion service and index the file into Qdrant.

2. **Check Logs (Troubleshooting)**:
   ```bash
   # View logs for the Backend service
   gcloud run services logs read enterprise-rag-backend --limit 50
   ```

3. **Total Shutdown (To stop billing)**:
   ```bash
   cd terraform
   /c/terraform/terraform.exe destroy
   ```

---
*Status: Ready for Production.* 🚀


```
gcloud builds submit --config cloudbuild.yaml .

```


```
cd terraform
/c/terraform/terraform.exe apply -auto-approve

```


CMD for single docker app 


```

gcloud run deploy rag-api \
  --source . \
  --region us-central1 \
  --timeout=300 \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=dmtxpress,LOCATION=us-central1,BUCKET_NAME=rag-enterprise-bucket,GROQ_API_KEY=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,QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6ODRiM2Y5MTAtMjExZC00MWZmLWJjOWUtMDVlZjEzYWVmZmVjIn0.f0qLRXyvjRRp5aP84Si1V2lh38q7Qy4SpOLtXYC7gDM,QDRANT_CLUSTER_ENDPOINT=https://ea091fa5-4283-45b8-bc40-633cc17426aa.us-east4-0.gcp.cloud.qdrant.io,REDIS_HOST=10.97.147.220,DB_USER=postgres,DB_PASS=Divesh.sql@000,DB_CONNECTION_NAME=dmtxpress:us-central1:rag-enterprise-db,LOGFIRE_TOKEN=pylf_v1_us_6Yz5SjlR2WdVdgvSbrr106FzpDD6nZkHhNjbCmLChzX5"


```

Manual data ingestion

```
python -m app.pipelines.ingestion.processor "DATA/true_data" "true"


python -m app.pipelines.ingestion.processor "DATA/true_data" "true"


```

with wipe parameter

```

python -m app.pipelines.ingestion.processor "DATA/noisy_data" "noisy" --wipe


```