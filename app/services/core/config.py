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

    # --- CACHE (REDIS) ---
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    USE_SEMANTIC_CACHE = os.getenv("USE_SEMANTIC_CACHE", "true").lower() == "true"

    # --- REASONING ENGINE (GROQ) ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"

    # --- PERSISTENCE (POSTGRES) ---
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")

    @property
    def DATABASE_URL(self):
        """
        Generates the psycopg3 connection string.
        Handles Cloud Run Unix Sockets vs Local TCP.
        """
        if self.DB_HOST.startswith("/cloudsql"):
            # Format for psycopg3 Unix socket: host=/path/to/socket
            return f"host={self.DB_HOST} dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASS}"
        
        # Format for Local TCP
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- OBSERVABILITY ---
    LANGSMITH_TRACING = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGSMITH_API_KEY = os.getenv("LANGCHAIN_API_KEY")

settings = Settings()
