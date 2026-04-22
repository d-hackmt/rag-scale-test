import os
from google.cloud import storage
from app.config import BUCKET_NAME, PROJECT_ID
from app.services.gcs_service import upload_vector_store # Re-export for convenience

def upload_chunks(chunks):
    """Uploads text chunks to the 'chunks/' folder in GCS."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    for chunk in chunks:
        blob = bucket.blob(f"chunks/{chunk['id']}.txt")
        blob.upload_from_string(chunk["text"])

    print(f"Uploaded {len(chunks)} chunks to GCS (Folder: chunks/)")

def upload_raw_documents(data_dir: str):
    """Uploads original PDF files to the 'raw/' folder in GCS."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    count = 0
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            local_path = os.path.join(data_dir, filename)
            blob = bucket.blob(f"raw/{filename}")
            blob.upload_from_filename(local_path)
            count += 1
    
    print(f"Uploaded {count} raw documents to GCS (Folder: raw/)")