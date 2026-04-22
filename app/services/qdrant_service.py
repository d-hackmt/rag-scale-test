import logfire
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION

# Initialize Qdrant Client with increased timeout for reliability
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

def ensure_collection(vector_size: int):
    """Ensures the Qdrant collection exists."""
    collections = client.get_collections().collections
    exists = any(c.name == QDRANT_COLLECTION for c in collections)
    
    if not exists:
        print(f"Creating collection: {QDRANT_COLLECTION}")
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

def upsert_vectors(vectors, metadata):
    """Upserts vectors and metadata to Qdrant in optimized batches."""
    ensure_collection(len(vectors[0]))
    
    points = [
        PointStruct(
            id=i, 
            vector=vectors[i], 
            payload={"text": metadata[i]}
        ) for i in range(len(vectors))
    ]
    
    # Batch processing to avoid timeouts
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        with logfire.span(f"Upserting Qdrant Batch {i//batch_size + 1}"):
            client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=batch
            )
        print(f"Upserted batch {i//batch_size + 1} ({len(batch)} points)")
    
    print(f"Successfully upserted {len(points)} total points to Qdrant.")


def search_qdrant(query_vector, k=5):
    """Searches Qdrant for the closest vectors."""
    with logfire.span("Searching Qdrant"):
        # The new Qdrant 1.17+ API uses 'query_points' instead of 'search'
        response = client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vector,
            limit=k
        )
        results = response.points
    
    return [hit.payload["text"] for hit in results]
