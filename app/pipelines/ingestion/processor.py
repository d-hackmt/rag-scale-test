import os
import uuid
import json
import logfire
import tempfile
from typing import List
from fastapi import FastAPI, Request
from google.cloud import storage
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from app.services.core.config import settings
from app.services.core.embedding import embed_texts
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize FastAPI
app = FastAPI()

# Initialize Logfire
logfire.configure()

# Initialize GCS
storage_client = storage.Client(project=settings.PROJECT_ID)

# Initialize Qdrant
client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    if not text.strip(): return []
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return [c for c in chunks if c.strip()]

def upload_to_gcs(data, bucket_name: str, destination_blob_name: str, is_json: bool = False):
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        if is_json:
            blob.upload_from_string(json.dumps(data), content_type='application/json')
        else:
            blob.upload_from_filename(data)
        logfire.info(f"☁️ Uploaded {destination_blob_name} to {bucket_name}")
    except Exception as e:
        logfire.error(f"❌ GCS Upload Failed ({destination_blob_name}): {e}")

def process_file_logic(local_path: str, filename: str, source_type: str = "auto"):
    """Core logic to process a single file and push to Qdrant."""
    try:
        logfire.info(f"📄 Processing: {filename}")
        
        # 1. Extract Text
        full_text = ""
        if filename.lower().endswith('.txt'):
            with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                full_text = f.read()
        else:
            elements = partition(filename=local_path, strategy="fast")
            full_text = "\n".join([str(el) for el in elements])
        
        if not full_text.strip(): return
        chunks = chunk_text(full_text)
        if not chunks: return

        # 2. Upload to PROCESSED Bucket
        processed_data = {"filename": filename, "chunks": chunks}
        processed_path = f"{source_type}/{filename}.json"
        upload_to_gcs(processed_data, settings.PROCESSED_BUCKET, processed_path, is_json=True)

        # 3. Embed and Index
        embeddings = embed_texts(chunks)
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            points.append(models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": chunk,
                    "source": filename,
                    "source_type": source_type,
                    "raw_gcs_path": f"gs://{settings.RAW_BUCKET}/{source_type}/{filename}"
                }
            ))
        
        if not client.collection_exists(settings.QDRANT_COLLECTION):
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
            )

        client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        logfire.info(f"✅ Fully Indexed: {filename}")
        
    except Exception as e:
        logfire.error(f"❌ Processing Error {filename}: {e}")

@app.get("/")
def health():
    return {"status": "Ingestion service is alive"}

@app.post("/")
async def handle_eventarc(request: Request):
    """
    Listens for GCS Eventarc signals and processes the new file.
    """
    event = await request.json()
    logfire.info(f"🔔 Received Eventarc Signal: {event}")
    
    bucket = event.get("bucket")
    name = event.get("name")
    
    if not bucket or not name:
        return {"message": "Invalid event data"}

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        # Download file from GCS
        storage_client.bucket(bucket).blob(name).download_to_filename(tmp.name)
        # Process it
        process_file_logic(tmp.name, name)
        os.unlink(tmp.name)
        
    return {"status": "success", "file": name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
