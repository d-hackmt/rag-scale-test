from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node
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

# --- MEMORY UPGRADE ---
# MemorySaver allows the agent to remember conversations based on 'thread_id'
checkpointer = MemorySaver()

# 4. Compile the Graph with Memory
rag_agent = workflow.compile(checkpointer=checkpointer)
