import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------- CONFIG --------
PROJECT_ID = os.getenv("PROJECT_ID", "dmtxpress")
BUCKET_NAME = os.getenv("BUCKET_NAME", "rag-learning-bucket-420")
LOCATION = os.getenv("LOCATION", "us-central1")

# Vector Store Config
FAISS_INDEX_PATH = "index.faiss"
METADATA_PATH = "metadata.pkl"
GCS_INDEX_BLOB = "vector_store/index.faiss"
GCS_METADATA_BLOB = "vector_store/metadata.pkl"
