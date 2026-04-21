import faiss
import numpy as np

index = None
documents_store = None


def build_index(embeddings, documents):
    global index, documents_store

    embeddings = np.array(embeddings)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    documents_store = documents


def search(query_embedding, k=2):
    D, I = index.search(np.array([query_embedding]), k)
    return [documents_store[i] for i in I[0]]