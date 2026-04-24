import time
import logfire
from google.cloud import discoveryengine_v1 as discoveryengine
from app.services.core.config import settings

def rerank_documents(query: str, documents: list[str], top_n: int = 5) -> list[str]:
    """
    Uses Vertex AI Ranking API to re-rank retrieved documents.
    """
    if not documents:
        return []

    start_time = time.time()
    logfire.info(f"📡 [Reranker] Sending {len(documents)} docs to Vertex AI Ranking API...")

    try:
        client = discoveryengine.RankServiceClient()
        
        # Default ranking config using our centralized settings
        ranking_config = f"projects/{settings.PROJECT_ID}/locations/global/rankingConfigs/default_ranking_config"

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

        response = client.rank(request=request)
        
        # Extract the content of the re-ranked documents
        reranked_docs = []
        for record in response.records:
            idx = int(record.id)
            reranked_docs.append(documents[idx])

        duration = time.time() - start_time
        logfire.info(f"✅ [Reranker] Done in {duration:.2f}s. Top result score: {response.records[0].score if response.records else 'N/A'}")
        
        return reranked_docs

    except Exception as e:
        logfire.error(f"❌ [Reranker] Error: {e}")
        return documents[:top_n] # Fallback to original order if API fails
