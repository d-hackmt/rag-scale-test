from google.cloud import storage
import os
from app.config import BUCKET_NAME, PROJECT_ID, GCS_INDEX_BLOB, GCS_METADATA_BLOB, FAISS_INDEX_PATH, METADATA_PATH

def get_storage_client():
    return storage.Client(project=PROJECT_ID)

def load_documents():
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)

    blobs = bucket.list_blobs(prefix="chunks/")
    documents = [blob.download_as_text() for blob in blobs]

    if not documents:
        raise Exception("No documents found in bucket")

    return documents

def upload_vector_store():
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)

    if os.path.exists(FAISS_INDEX_PATH):
        blob = bucket.blob(GCS_INDEX_BLOB)
        blob.upload_from_filename(FAISS_INDEX_PATH)
    
    if os.path.exists(METADATA_PATH):
        blob = bucket.blob(GCS_METADATA_BLOB)
        blob.upload_from_filename(METADATA_PATH)

def download_vector_store():
    client = get_storage_client()
    bucket = client.bucket(BUCKET_NAME)

    index_blob = bucket.blob(GCS_INDEX_BLOB)
    if index_blob.exists():
        index_blob.download_to_filename(FAISS_INDEX_PATH)
    
    metadata_blob = bucket.blob(GCS_METADATA_BLOB)
    if metadata_blob.exists():
        metadata_blob.download_to_filename(METADATA_PATH)
    
    return os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH)