# Component-by-Component Roadmap

Here is the breakdown of what is remaining to reach the target "Enterprise RAG" architecture.

## 1. Data Ingestion (Graph + Vector)
- **Status**: Basic Vector Chunking (Done).
- **Missing**: Graph Extraction.
- **Next Steps**:
  - Integrate `langchain-neo4j` or custom logic to extract entities (Nodes) and relationships (Edges).
  - Push vectors to Qdrant Collection instead of local FAISS files.

## 2. Multi-Sub Agents (Orchestration)
- **Status**: Single Query-Context Flow (Done).
- **Missing**: Planner, Graph Searcher, Vector Searcher.
- **Next Steps**:
  - Implement a **Planner Agent** that decides whether to look in the Graph (for relationships) or Vector (for semantics) database.
  - Create specialized searcher agents for each data source.

## 3. Serving Layer (API Gateway & Cache)
- **Status**: Raw FastAPI on Cloud Run (Done).
- **Missing**: Caching & Gateway.
- **Next Steps**:
  - Add **Redis** integration in `app/services/vector_store.py` to cache query results.
  - Configure **API Gateway** to handle rate limiting and security headers.

## 4. Monitoring & Evaluation
- **Status**: Basic print statements (Done).
- **Missing**: Logging, Tracing, Evaluation Reports.
- **Next Steps**:
  - Use **LangSmith** or **Pydantic Logfire** for full-stack observability.
  - Implement an evaluation pipeline using **RAGAS** to score accuracy and faithfulness.

## New Files to Add
- `app/services/qdrant_service.py`: To replace `vector_store.py` logic.
- `app/services/graph_service.py`: To handle Neo4j queries.
- `app/agents/planner.py`: For multi-agent orchestration.
- `app/api/v1/auth.py`: For user authentication logic.
- `terraform/`: Directory containing `.tf` files for GKE, Cloud SQL, and Memorystore setup.

## Progress Checklist
- [x] GCS Document Storage
- [x] Vertex AI Embedding Integration
- [x] Basic Streamlit UI
- [ ] Qdrant Cloud/GKE Integration
- [ ] Neo4j Graph Integration
- [ ] Multi-Agent Planner Implementation
- [ ] Redis Caching Layer
- [ ] Auth & API Gateway
- [ ] Enterprise Observability (Prometheus/Grafana)
