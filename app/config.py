import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------- GCP CONFIG --------
PROJECT_ID = os.getenv("PROJECT_ID", "dmtxpress")
BUCKET_NAME = os.getenv("BUCKET_NAME", "rag-enterprise-bucket")
LOCATION = os.getenv("LOCATION", "us-central1")

# -------- QDRANT CONFIG --------
QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = "document_chunks"

# -------- REDIS CONFIG --------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# -------- POSTGRES CONFIG --------
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_CONNECTION_NAME = os.getenv("DB_CONNECTION_NAME")

# -------- LOGFIRE CONFIG --------
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")

# Legacy FAISS Config (kept for fallback compatibility temporarily)
FAISS_INDEX_PATH = "index.faiss"
METADATA_PATH = "metadata.pkl"
GCS_INDEX_BLOB = "vector_store/index.faiss"
GCS_METADATA_BLOB = "vector_store/metadata.pkl"
