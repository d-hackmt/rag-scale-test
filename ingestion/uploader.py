from google.cloud import storage
from app.config import BUCKET_NAME, PROJECT_ID
from app.services.gcs_service import upload_vector_store # Re-export for convenience

def upload_chunks(chunks):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    for chunk in chunks:
        blob = bucket.blob(f"chunks/{chunk['id']}.txt")
        blob.upload_from_string(chunk["text"])

    print(f"Uploaded {len(chunks)} chunks to GCS")