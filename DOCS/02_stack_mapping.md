# AWS to GCP Stack Mapping Guide

Based on the goal architecture, here is how we translate the AWS components to their modern GCP equivalents.

## Architectural Comparison

| Layer | AWS (Original) | GCP (Replacement) | Why? |
| :--- | :--- | :--- | :--- |
| **Storage** | S3 | **Cloud Storage (GCS)** | Native blob storage with similar latency and cost. |
| **Compute** | EC2 / EKS | **GKE (Google Kubernetes Engine)** | Standardized orchestration for scalable microservices. |
| **Serverless** | Lambda | **Cloud Run** | Better for containerized APIs (FastAPI) than pure Lambda. |
| **Vector DB** | Qdrant (Self-hosted) | **Qdrant (GKE) or Vertex Vector Search** | Enterprise-grade vector similarity search. |
| **Graph DB** | Neo4j | **Neo4j Aura or GKE** | Industry standard for Knowledge Graphs. |
| **Cache** | Redis | **Cloud Memorystore** | Managed Redis with high availability. |
| **DB** | Aurora Postgres | **Cloud SQL (Postgres)** | Fully managed relational database. |
| **Model Serving** | Ray + vLLM | **GKE or Vertex AI Model Garden** | Scalable serving for large language models. |
| **Monitoring** | Grafana | **Cloud Monitoring + Grafana (GKE)** | Deep integration with GCP metrics. |

## Target Architecture Diagram
```mermaid
graph TD
    User((User)) -->|Query| LB[Cloud Load Balancer]
    LB --> Gateway[Cloud API Gateway]
    Gateway --> Agent[Orchestration Agent - GKE]
    
    subgraph "Knowledge Retrieval"
        Agent -->|Vector Search| Qdrant[(Qdrant DB)]
        Agent -->|Graph Search| Neo4j[(Neo4j DB)]
        Agent -->|SQL Search| CloudSQL[(Cloud SQL)]
    end
    
    subgraph "Execution"
        Agent -->|Prompt| LLM[Vertex AI Gemini]
        Agent -->|Cache| Redis[(Memorystore)]
    end
    
    Agent -->|Tracing| Monitoring[Cloud Monitoring / LangSmith]
```
