# ⚙️ Ingestion Engine (Event-Driven)

The ingestion pipeline is now a fully automated, event-driven microservice.

## 🔄 Automatic Workflow
1.  **GCS Upload**: A file is uploaded to the `${project_id}-rag-raw` bucket.
2.  **Event Signal**: GCP Eventarc detects the upload and sends a POST request to the **Ingestion Worker**.
3.  **Processing**:
    -   **Partitioning**: Uses `unstructured` to extract text from PDF/Docx.
    -   **Embedding**: Generates vectors using Vertex AI.
    -   **Indexing**: Upserts vectors and metadata into **Qdrant**.
4.  **Storage**: Moves a JSON version of the chunks to the `${project_id}-rag-processed` bucket for auditing.

## 🛠️ Manual Execution (For Testing)
If you need to run ingestion manually within the cloud:
```bash
gcloud builds submit --config cloudbuild-ingestion.yaml .
```

---
*Status: Fully automated via Eventarc.*
