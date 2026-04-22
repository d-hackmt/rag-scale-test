import os
import logfire
import uuid
import time
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from app.services.qdrant_service import search_qdrant
from app.services.embedding import get_embedding_model
from app.services.ranking_service import rerank_documents
from app.services.redis_service import get_cache, set_cache, add_to_history, get_session_history
from app.services.database_service import log_query_to_db
from app.config import PROJECT_ID, LOCATION

# Set standard Google Cloud environment variables for pydantic-ai auto-detection
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

# --- Structured Response Schemas ---

class ToolCall(BaseModel):
    tool_name: str = Field(description="The name of the tool called")
    query: str = Field(description="The search query used")
    summary: str = Field(description="Key findings from this specific search")

class RAGResponse(BaseModel):
    reasoning: str = Field(description="Internal thought process: why did you choose these sources? Did you need to search multiple times?")
    answer: str = Field(description="The final, concise, and accurate answer based ONLY on the provided context.")
    sources: list[str] = Field(description="Direct snippets or URLs used to verify the answer")
    tool_history: list[ToolCall] = Field(description="Log of all searches performed")

# Define the RAG Agent
rag_agent = Agent(
    model='groq:llama-3.3-70b-versatile',
    output_type=RAGResponse,
    retries=5,
    system_prompt=(
        "You are an Elite Enterprise RAG Assistant. Your primary goal is ACCURACY. "
        "### Operational Rules:\n"
        "1. **Analyze First**: Before calling any tool, analyze if the user's question requires external data.\n"
        "2. **Search Deeply**: If the first search is too broad or yields no results, try a more specific query.\n"
        "3. **Verify Context**: Only answer based on the retrieved context. If the information is not there, state: 'I don't have enough information in the current documents to answer this accurately.'\n"
        "4. **Strict Output**: Your final response must be PURE JSON matching the RAGResponse schema. "
        "CRITICAL: Do NOT wrap your response in <function>, <final_result>, or any XML tags. Just return the JSON object.\n"
        "5. **Reasoning**: Use the 'reasoning' field to explain your logic."
    ),
)

@rag_agent.tool
async def search_vector_db(ctx: RunContext[None], query: str) -> list[str]:
    """Search the enterprise vector database for precise technical information."""
    embed_model = get_embedding_model()
    q_emb_resp = embed_model.get_embeddings([query])
    q_emb = q_emb_resp[0].values
    
    with logfire.span(f"Searching Qdrant for: {query}"):
        initial_results = search_qdrant(q_emb, k=25) 
    
    with logfire.span("Vertex AI Semantic Re-ranking"):
        final_results = rerank_documents(query, initial_results, top_n=5)
        
    return final_results

async def run_agent_query(user_query: str, session_id: str = "default"):
    """Entry point to run a query through the Pydantic AI Agent with Caching and Logging."""
    start_time = time.time()
    
    # 1. Check Semantic Cache in Redis
    cached_result = get_cache(f"query:{user_query}")
    if cached_result:
        print(f"🚀 Semantic Cache Hit for: {user_query}")
        return cached_result

    # 2. Retrieve Session History
    history = get_session_history(session_id)
    
    with logfire.span("Agent Orchestration"):
        # We include history in the message sequence if needed
        # For now, we'll run a fresh query but we could append history here
        result = await rag_agent.run(user_query)
        output_dict = result.output.model_dump()
        
        latency = time.time() - start_time
        query_id = str(uuid.uuid4())

        # 3. Save to Semantic Cache
        set_cache(f"query:{user_query}", output_dict)

        # 4. Update Session History
        add_to_history(session_id, {"role": "user", "content": user_query})
        add_to_history(session_id, {"role": "assistant", "content": output_dict["answer"]})

        # 5. Log to Postgres (Audit Trail)
        log_query_to_db(
            query_id=query_id,
            query_text=user_query,
            reasoning=output_dict["reasoning"],
            answer=output_dict["answer"],
            sources=output_dict["sources"],
            latency=latency
        )

        return output_dict
