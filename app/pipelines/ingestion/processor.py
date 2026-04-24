import os
import uuid
import json
import logfire
from typing import List
from google.cloud import storage
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from app.services.core.config import settings
from app.services.core.embedding import embed_texts
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Initialize Logfire
logfire.configure()

# Initialize GCS
storage_client = storage.Client(project=settings.PROJECT_ID)

# Initialize Qdrant
client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def upload_to_gcs(data, bucket_name: str, destination_blob_name: str, is_json: bool = False):
    """Uploads a file or JSON data to GCS."""
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

def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    """Simple semantic-ish chunker."""
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

def ingest_directory(dir_path: str, source_type: str = "general", wipe: bool = False):
    """
    Scans a directory, fills Raw & Processed buckets, and indexes Qdrant.
    """
    logfire.info(f"🚀 Starting Enterprise Ingestion: {dir_path} ({source_type})")
    
    if wipe and client.collection_exists(settings.QDRANT_COLLECTION):
        client.delete_collection(settings.QDRANT_COLLECTION)

    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
        )

    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if not filename.lower().endswith(('.pdf', '.docx', '.pptx', '.txt')):
            continue

        try:
            logfire.info(f"📄 Processing: {filename}")
            
            # 1. Upload to RAW Bucket
            raw_path = f"{source_type}/{filename}"
            upload_to_gcs(file_path, settings.RAW_BUCKET, raw_path)
            
            # 2. Extract Text with Fallback
            full_text = ""
            if filename.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    full_text = f.read()
            else:
                try:
                    # Attempt standard high-speed partitioning
                    elements = partition(filename=file_path, strategy="fast")
                    full_text = "\n".join([str(el) for el in elements])
                except Exception as e:
                    logfire.warning(f"⚠️ Advanced parser failed for {filename}, falling back to basic PDF text extraction...")
                    # Fallback for PDF specifically if unstructured_inference is missing
                    if filename.lower().endswith('.pdf'):
                        elements = partition_pdf(filename=file_path, strategy="fast")
                        full_text = "\n".join([str(el) for el in elements])
                    else:
                        raise e
            
            if not full_text.strip(): continue
            chunks = chunk_text(full_text)
            if not chunks: continue

            # 3. Upload to PROCESSED Bucket
            processed_data = {"filename": filename, "chunks": chunks}
            processed_path = f"{source_type}/{filename}.json"
            upload_to_gcs(processed_data, settings.PROCESSED_BUCKET, processed_path, is_json=True)

            # 4. Embed and Index
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
                        "raw_gcs_path": f"gs://{settings.RAW_BUCKET}/{raw_path}"
                    }
                ))
            
            client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
            logfire.info(f"✅ Fully Processed: {filename}")
            
        except Exception as e:
            logfire.error(f"❌ Failed {filename}: {e}")

if __name__ == "__main__":
    import sys
    wipe_requested = "--wipe" in sys.argv
    clean_args = [a for a in sys.argv if a != "--wipe"]
    if len(clean_args) < 3:
        print("Usage: python -m app.pipelines.ingestion.processor <dir_path> <source_type> [--wipe]")
        sys.exit(1)
    ingest_directory(clean_args[1], clean_args[2], wipe=wipe_requested)
