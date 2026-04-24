import re
import logfire

def clean_text(text: str) -> str:
    """
    Standardizes text by removing extra whitespace and special characters.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_gcs_link(bucket: str, path: str) -> str:
    """
    Formats a standard GCS URI.
    """
    return f"gs://{bucket}/{path}"

def validate_config(settings):
    """
    Ensures all critical environment variables are loaded.
    """
    required = ["PROJECT_ID", "QDRANT_URL", "GROQ_API_KEY"]
    missing = [field for field in required if not getattr(settings, field, None)]
    
    if missing:
        logfire.error(f"❌ Missing critical config: {missing}")
        return False
    return True
