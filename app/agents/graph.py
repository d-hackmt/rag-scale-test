import os
import logfire
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node
from app.services.core.config import settings

# Initialize Logfire
try:
    logfire.configure()
except Exception:
    pass

# 1. Initialize the State Graph
workflow = StateGraph(AgentState)
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("responder", generate_node)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "retriever")
workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END)

# --- MEMORY: Postgres (Cloud Ready) ---
try:
    # Use the pre-built DATABASE_URL from config.py
    # It automatically handles the Unix socket for Cloud Run
    if settings.DB_PASS:
        pool = ConnectionPool(
            conninfo=settings.DATABASE_URL,
            max_size=10,
            kwargs={"autocommit": True}
        )
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        logfire.info("📡 Postgres Connection Pool Active & Tables Ready")
    else:
        raise ValueError("DB_PASS missing")

except Exception as e:
    logfire.warn(f"⚠️ Persistence Connection Failed: {e}. Falling back to In-Memory.")
    checkpointer = MemorySaver()

# 4. Compile the Graph
rag_agent = workflow.compile(checkpointer=checkpointer)
