from fastapi import FastAPI
from app.agent import run_agent_query
import vertexai
from app.config import PROJECT_ID, LOCATION, LOGFIRE_TOKEN
import logfire

# Initialize Logfire
if LOGFIRE_TOKEN:
    logfire.configure(token=LOGFIRE_TOKEN)
else:
    logfire.configure() # Fallback to local console logging

vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()
logfire.instrument_fastapi(app)


@app.get("/")
def home():
    return {"message": "Enterprise Agentic RAG API is running"}


@app.get("/query")
async def query(q: str):
    # run_agent_query now returns a dict {answer: ..., sources: ..., graph_knowledge: ..., tool_history: ...}
    result = await run_agent_query(q)
    return {
        "question": q,
        **result
    }