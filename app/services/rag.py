from app.services.gcs_service import load_documents
from app.services.embedding import embed_texts, get_embedding_model
from app.services.vector_store import build_index, search
from app.services.llm import generate_answer

initialized = False


def initialize():
    global initialized

    if initialized:
        return

    print("Loading documents...")
    docs = load_documents()

    print("Creating embeddings...")
    embeddings = embed_texts(docs)

    print("Building index...")
    build_index(embeddings, docs)

    initialized = True
    print("RAG system ready!")


def query_rag(query):
    initialize()

    model = get_embedding_model()
    q_emb = model.get_embeddings([query])[0].values

    retrieved_docs = search(q_emb)

    context = "\n".join(retrieved_docs)

    answer = generate_answer(query, context)

    return {
        "question": query,
        "answer": answer,
        "context": retrieved_docs
    }