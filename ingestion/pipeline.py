from ingestion.pdf_loader import load_pdfs
from ingestion.chunking import chunk_documents
from ingestion.uploader import upload_chunks

def run_pipeline():
    print("Loading PDFs...")
    docs = load_pdfs("DATA")

    print("Chunking...")
    chunks = chunk_documents(docs)

    print("Uploading to GCS...")
    upload_chunks(chunks)

    print("Ingestion complete!")


if __name__ == "__main__":
    run_pipeline()