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