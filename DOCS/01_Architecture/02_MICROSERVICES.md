# 🧩 Microservices Architecture

This project is built on a **Decoupled 3-Tier Architecture**. By splitting the system into microservices, we ensure that the UI can scale independently of the Backend, and the Ingestion worker only runs when needed (saving costs).

---

## 1. The Frontend (UI Service)
- **Technology**: Streamlit
- **Role**: Handles user interaction, chat history rendering, and visualization of the agent's "Thought Process."
- **Cloud Run Port**: 8501
- **Connection**: Communicates with the Backend via a secure internal HTTP request (`BACKEND_URL`).

## 2. The Brain (Backend API Service)
- **Technology**: FastAPI + LangGraph
- **Role**: The orchestrator. It receives queries, runs the LangGraph planner, calls the LLM (Groq), and retrieves data from Qdrant.
- **Memory**: Connects to **Cloud SQL (Postgres)** via a connection pool to persist conversation state across threads.
- **Cloud Run Port**: 8080

## 3. The Worker (Ingestion Service)
- **Technology**: FastAPI + Unstructured.io
- **Role**: A "Cloud-Native" worker that wakes up only when an event is triggered. It downloads new files from GCS, partitions them into chunks, embeds them, and upserts them to Qdrant.
- **Trigger**: Activated by **Eventarc** via a `POST` request.
- **Cloud Run Port**: 8080

---

## 🚀 Scaling Strategy
- **Concurrency**: Each service can handle multiple simultaneous requests.
- **Auto-Scaling**: Cloud Run automatically scales from 0 to 100+ instances based on traffic.
- **Cold Starts**: The Ingestion worker is designed to scale to 0 when not in use, ensuring you only pay for the seconds it spends processing a file.
