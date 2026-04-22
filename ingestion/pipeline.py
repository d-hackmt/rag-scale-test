from ingestion.pdf_loader import load_pdfs
from ingestion.chunking import chunk_documents
from ingestion.uploader import upload_chunks, upload_raw_documents
from app.services.embedding import embed_texts
from app.services.qdrant_service import upsert_vectors
import vertexai
from app.config import PROJECT_ID, LOCATION, LOGFIRE_TOKEN, BUCKET_NAME
from google.cloud import storage
import logfire
import json

# Initialize Logfire
if LOGFIRE_TOKEN:
    logfire.configure(token=LOGFIRE_TOKEN)
else:
    logfire.configure()

def run_pipeline():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("Step 1: Backup Raw Documents...")
    upload_raw_documents("DATA")

    print("Step 2: Processing Content...")
    docs = load_pdfs("DATA")
    chunks = chunk_documents(docs)

    print("Step 3: Storing Chunks in GCS...")
    upload_chunks(chunks)

    print("Step 4: Vector Processing (Qdrant)...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    # This handles batching and timeouts internally
    upsert_vectors(embeddings, texts)

    print("Step 5: Finalizing Backups...")
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    status_blob = bucket.blob("backups/last_ingestion.json")
    status_blob.upload_from_string(json.dumps({
        "status": "success",
        "total_chunks": len(chunks),
        "total_documents": len(docs),
        "mode": "vector-only"
    }))

    print("✅ Vector Ingestion fully complete!")

if __name__ == "__main__":
    run_pipeline()
