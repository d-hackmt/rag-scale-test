from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node
from app.services.core.config import settings
import logfire

# 1. Initialize the State Graph
workflow = StateGraph(AgentState)

# 2. Define the Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("responder", generate_node)

# 3. Define the Edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "retriever")
workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END)

# --- MEMORY UPGRADE: Postgres (Cloud Ready) ---
# We use a connection pool for high-concurrency Cloud Run scaling
try:
    if settings.DB_PASS: # Check if DB credentials exist
        pool = ConnectionPool(
            conninfo=settings.DATABASE_URL,
            max_size=20,
            kwargs={"autocommit": True}
        )
        checkpointer = PostgresSaver(pool)
        # Note: In a real production environment, you'd run checkpointer.setup() 
        # as part of a migration, but here we'll ensure tables exist.
        logfire.info("📡 Connecting to Postgres Checkpointer...")
    else:
        raise ValueError("No DB_PASS found in environment.")

except Exception as e:
    logfire.warn(f"⚠️ Postgres Memory Connection Failed: {e}. Falling back to local MemorySaver.")
    checkpointer = MemorySaver()

# 4. Compile the Graph with Memory
rag_agent = workflow.compile(checkpointer=checkpointer)
