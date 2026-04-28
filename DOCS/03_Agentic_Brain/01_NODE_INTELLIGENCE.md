# 🧠 Agentic Brain & Memory

The reasoning engine uses **LangGraph** to coordinate between planning, retrieval, and response generation.

## 💾 Production Memory: Postgres
Unlike prototypes that use RAM (`MemorySaver`), this enterprise version uses **Cloud SQL (Postgres)**.
-   **Thread Persistence**: Conversation history is stored in the `rag_memory` database.
-   **Session Resumption**: Users can return to a conversation hours later, and the agent will remember the context.
-   **Horizontal Scaling**: Since memory is in a database (not local RAM), we can run 100+ instances of the Backend service, and they will all share the same agent memory.

## 🤖 Reasoning Nodes
1.  **Planner**: Decides the strategy based on the query.
2.  **Retriever**: Fetches relevant data from Qdrant.
3.  **Responder**: Synthesizes the final answer using Groq Llama 3.3.

---
*Status: Production-grade persistence active.*
