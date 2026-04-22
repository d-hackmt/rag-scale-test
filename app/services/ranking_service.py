import time
import logfire
from google.cloud import discoveryengine_v1 as discoveryengine
from app.config import PROJECT_ID, LOCATION

def rerank_documents(query: str, documents: list[str], top_n: int = 5) -> list[str]:
    """
    Uses Vertex AI Ranking API to re-rank retrieved documents.
    """
    if not documents:
        return []

    start_time = time.time()
    print(f"\n📡 [Reranker] Sending {len(documents)} documents to Vertex AI Ranking API...")

    try:
        client = discoveryengine.RankServiceClient()
        
        # Default ranking config
        ranking_config = f"projects/{PROJECT_ID}/locations/global/rankingConfigs/default_ranking_config"

        records = [
            discoveryengine.RankingRecord(id=str(i), content=doc)
            for i, doc in enumerate(documents)
        ]

        request = discoveryengine.RankRequest(
            ranking_config=ranking_config,
            model="semantic-ranker-512@latest",
            top_n=top_n,
            query=query,
            records=records,
        )

        with logfire.span("Vertex AI Re-ranking Request"):
            response = client.rank(request=request)
        
        ranked_docs = [documents[int(result.id)] for result in response.records]
        
        duration = time.time() - start_time
        print(f"✅ [Reranker] Success! Took {duration:.2f} seconds.")
        return ranked_docs

    except Exception as e:
        print(f"❌ [Reranker] API Error: {e}. Falling back to original order.")
        return documents[:top_n]
