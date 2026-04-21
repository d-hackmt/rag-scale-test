from app.services.gcs_service import load_documents, download_vector_store
from app.services.embedding import embed_texts, get_embedding_model
from app.services.vector_store import build_index, search, load_index
from app.services.llm import generate_answer
import os

initialized = False


def initialize():
    global initialized

    if initialized:
        return

    print("Checking for existing vector store in GCS...")
    if download_vector_store():
        print("Loading index from GCS...")
        if load_index():
            initialized = True
            print("RAG system ready (loaded from GCS)!")
            return

    # Fallback to building from documents if index not found
    print("Index not found in GCS. Falling back to document loading and embedding...")
    docs = load_documents()

    print("Creating embeddings...")
    embeddings = embed_texts(docs)

    print("Building index...")
    build_index(embeddings, docs)

    initialized = True
    print("RAG system ready (built from documents)!")


def query_rag(query):
    initialize()

    model = get_embedding_model()
    # Vertex AI embeddings often return a list of values
    q_emb_response = model.get_embeddings([query])
    q_emb = q_emb_response[0].values

    retrieved_docs = search(q_emb)

    context = "\n".join(retrieved_docs)

    answer = generate_answer(query, context)

    return {
        "question": query,
        "answer": answer,
        "context": retrieved_docs
    }