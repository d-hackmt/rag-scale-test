from fastapi import FastAPI
from app.services.rag import query_rag
import vertexai
from app.config import PROJECT_ID, LOCATION

vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "RAG API with LLM is running"}


@app.get("/query")
def query(q: str):
    return query_rag(q)