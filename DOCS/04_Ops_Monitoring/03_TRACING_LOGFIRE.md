# 📈 Observability & Tracing

Enterprise systems require "X-Ray Vision" into their logic. We use **Logfire** and **Google Cloud Logging**.

## 🔍 Distributed Tracing (Logfire)
We have instrumented every layer of the system:
-   **UI**: Traces the user's initial click and the connection to the backend.
-   **LangGraph**: Traces every node transition (Planner -> Retriever -> Responder).
-   **Database**: Tracks the latency of memory retrieval from Postgres.

## 📊 Cloud Monitoring
-   **GCP Logs Explorer**: View real-time logs from all 3 microservices in one place.
-   **Error Reporting**: GCP will automatically notify you if a service crashes or an LLM call fails.

---
*Status: Full-stack instrumentation active.*
