import faiss
import numpy as np
import pickle
import os
from app.config import FAISS_INDEX_PATH, METADATA_PATH

index = None
documents_store = None


def build_index(embeddings, documents):
    global index, documents_store

    embeddings = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    documents_store = documents


def save_index(local_index_path=FAISS_INDEX_PATH, local_metadata_path=METADATA_PATH):
    global index, documents_store
    if index is not None:
        faiss.write_index(index, local_index_path)
    if documents_store is not None:
        with open(local_metadata_path, "wb") as f:
            pickle.dump(documents_store, f)


def load_index(local_index_path=FAISS_INDEX_PATH, local_metadata_path=METADATA_PATH):
    global index, documents_store
    if os.path.exists(local_index_path):
        index = faiss.read_index(local_index_path)
    if os.path.exists(local_metadata_path):
        with open(local_metadata_path, "rb") as f:
            documents_store = pickle.load(f)
    return index is not None and documents_store is not None


def search(query_embedding, k=2):
    global index, documents_store
    if index is None or documents_store is None:
        raise ValueError("Index or documents store not loaded. Call load_index first.")
    
    D, I = index.search(np.array([query_embedding]).astype('float32'), k)
    return [documents_store[i] for i in I[0] if i < len(documents_store)]