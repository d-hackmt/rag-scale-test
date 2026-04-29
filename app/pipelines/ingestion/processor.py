import os
import uuid
import json
import logfire
import tempfile
from typing import List
from fastapi import FastAPI, Request
from google.cloud import storage
from unstructured.partition.auto import partition
from app.services.core.config import settings
from app.services.core.embedding import embed_texts
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize FastAPI
app = FastAPI()

# Initialize Logfire
try:
    logfire.configure()
except Exception:
    pass

def get_clients():
    """Lazy initialization of clients to prevent startup crashes."""
    s_client = storage.Client(project=settings.PROJECT_ID)
    q_client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    return s_client, q_client

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

def process_file_logic(local_path: str, filename: str, source_type: str = "auto"):
    s_client, q_client = get_clients()
    try:
        logfire.info(f"📄 Processing: {filename}")
        
        # 1. Extract Text
        full_text = ""
        if filename.lower().endswith('.txt'):
            with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                full_text = f.read()
        else:
            # Standard partitioning
            elements = partition(filename=local_path, strategy="fast")
            full_text = "\n".join([str(el) for el in elements])
        
        if not full_text.strip(): return
        chunks = chunk_text(full_text)
        if not chunks: return

        # 2. Upload to PROCESSED
        processed_data = {"filename": filename, "chunks": chunks}
        processed_path = f"{source_type}/{filename}.json"
        s_client.bucket(settings.PROCESSED_BUCKET).blob(processed_path).upload_from_string(
            json.dumps(processed_data), content_type='application/json'
        )

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
        
        if not q_client.collection_exists(settings.QDRANT_COLLECTION):
            q_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
            )

        q_client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        logfire.info(f"✅ Fully Indexed: {filename}")
        
    except Exception as e:
        logfire.error(f"❌ Processing Error {filename}: {e}")

@app.get("/")
def health():
    return {"status": "Ingestion service is alive"}

@app.post("/")
async def handle_eventarc(request: Request):
    try:
        event = await request.json()
        logfire.info(f"🔔 Received Eventarc Signal: {event}")
        
        bucket = event.get("bucket")
        name = event.get("name")
        
        if not bucket or not name:
            return {"message": "Invalid event data"}

        s_client, _ = get_clients()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            s_client.bucket(bucket).blob(name).download_to_filename(tmp.name)
            process_file_logic(tmp.name, name)
            os.unlink(tmp.name)
            
        return {"status": "success", "file": name}
    except Exception as e:
        logfire.error(f"❌ Eventarc Handler Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
