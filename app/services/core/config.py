import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # --- GCP CONFIG ---
    PROJECT_ID = os.getenv("PROJECT_ID", "dmtxpress")
    LOCATION = os.getenv("LOCATION", "us-central1")
    GCP_DOC_AI_PROCESSOR_ID = os.getenv("GCP_DOC_AI_PROCESSOR_ID")
    RAW_BUCKET = os.getenv("GCP_RAW_BUCKET", "rag-data-raw")
    PROCESSED_BUCKET = os.getenv("GCP_PROCESSED_BUCKET", "rag-data-processed")

    # --- VECTOR DB (QDRANT) ---
    QDRANT_URL = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = "enterprise_rag_v2"

    # --- REASONING ENGINE (GROQ) ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"

    # --- PERSISTENCE (POSTGRES) ---
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_CONNECTION_NAME = os.getenv("DB_CONNECTION_NAME")

    # --- CACHE (REDIS) ---
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # --- OBSERVABILITY ---
    LANGSMITH_TRACING = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGSMITH_API_KEY = os.getenv("LANGCHAIN_API_KEY")

settings = Settings()
