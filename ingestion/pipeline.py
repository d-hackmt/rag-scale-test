from ingestion.pdf_loader import load_pdfs
from ingestion.chunking import chunk_documents
from ingestion.uploader import upload_chunks, upload_vector_store
from app.services.embedding import embed_texts
from app.services.vector_store import build_index, save_index
import vertexai
from app.config import PROJECT_ID, LOCATION

def run_pipeline():
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    print("Loading PDFs...")
    docs = load_pdfs("DATA")

    print("Chunking...")
    chunks = chunk_documents(docs)

    print("Uploading text chunks to GCS...")
    upload_chunks(chunks)

    print("Generating embeddings...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    print("Building FAISS index...")
    build_index(embeddings, texts)

    print("Saving index locally...")
    save_index()

    print("Uploading FAISS index to GCS...")
    upload_vector_store()

    print("Ingestion complete!")


if __name__ == "__main__":
    run_pipeline()