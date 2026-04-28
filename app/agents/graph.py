import os
import logfire
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from google.cloud.sql.connector import Connector, IPTypes
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node
from app.services.core.config import settings

# Initialize Logfire
logfire.configure()

def get_connection():
    """Official Cloud SQL Connector for 100% reliable production connection."""
    connector = Connector()
    conn = connector.connect(
        settings.DB_CONNECTION_NAME,
        "pg8000",
        user=settings.DB_USER,
        password=settings.DB_PASS,
        db=settings.DB_NAME,
        ip_type=IPTypes.PUBLIC # Cloud Run can reach Public IP via Proxy
    )
    return conn

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
    if settings.DB_CONNECTION_NAME and "localhost" not in settings.DB_HOST:
        # Use a Lazy Pool with the Connector
        pool = ConnectionPool(
            conninfo="",
            getconn=get_connection,
            max_size=10,
            kwargs={"autocommit": True}
        )
        checkpointer = PostgresSaver(pool)
        logfire.info("📡 Cloud SQL Connector Active")
    else:
        # Local Fallback
        pool = ConnectionPool(conninfo=settings.DATABASE_URL, max_size=5, kwargs={"autocommit": True})
        checkpointer = PostgresSaver(pool)
        logfire.info("🏠 Local Postgres Active")

except Exception as e:
    logfire.warn(f"⚠️ Persistence Connection Failed: {e}. Falling back to In-Memory.")
    checkpointer = MemorySaver()

# 4. Compile the Graph
rag_agent = workflow.compile(checkpointer=checkpointer)
