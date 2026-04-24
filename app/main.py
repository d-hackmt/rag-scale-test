from fastapi import FastAPI, Response
from app.agents.graph import rag_agent
from app.services.core.config import settings
import logfire

# Initialize Observability
logfire.configure()

app = FastAPI(title="Enterprise Agentic RAG")
# logfire.instrument_fastapi(app) # Disabled due to version conflict

@app.get("/")
def home():
    return {"message": "Enterprise LangGraph RAG API is live."}

@app.get("/graph")
def get_graph_image():
    """
    Returns the Mermaid image of the agent's workflow.
    """
    try:
        png_bytes = rag_agent.get_graph().draw_mermaid_png()
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        return {"error": f"Could not generate graph image: {e}"}

@app.get("/query")
async def query(q: str, thread_id: str = "default_user"):
    """
    Executes the LangGraph RAG flow with memory.
    """
    initial_state = {
        "messages": [{"role": "user", "content": q}],
        "current_query": q,
        "documents": [],
        "plan": ["Start"],
        "status": "Initializing Graph..."
    }
    
    # Configuration for Memory (Thread ID)
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run the graph with config
    final_output = await rag_agent.ainvoke(initial_state, config=config)
    
    return {
        "question": q,
        "answer": final_output.get("final_answer"),
        "thought_process": final_output.get("plan"),
        "status": final_output.get("status")
    }