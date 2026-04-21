from google.cloud import storage
from app.config import BUCKET_NAME , PROJECT_ID

def load_documents():
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)

    blobs = bucket.list_blobs(prefix="chunks/")
    documents = [blob.download_as_text() for blob in blobs]

    if not documents:
        raise Exception("No documents found in bucket")

    return documents