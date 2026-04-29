# 🐛 Error History & Debugging Log

Building a production-grade cloud system is a battle. Here are the major roadblocks we hit during development and how we conquered them.

## 1. The Qdrant "Import Time" Crash
**The Problem:** When deploying to Cloud Run, the container would crash immediately on startup.
**The Cause:** Our Python code was trying to connect to Qdrant the exact millisecond the file was imported (`client = QdrantClient(...)` at the top of the file). If the network was even slightly slow, Cloud Run killed the container.
**The Fix:** We implemented **Lazy Initialization**. We wrapped the connection in a function (`get_qdrant_client()`) so it only connects *when a query is actually made*.

## 2. Cloud SQL Connection Chaos (`psycopg` vs `pg8000`)
**The Problem:** The app crashed when trying to connect to Postgres.
**The Cause:** We had a major driver mismatch. We were using the Google Cloud SQL Connector library configured for the `pg8000` driver, but our `ConnectionPool` was built using `psycopg3`. They didn't speak the same language.
**The Fix:** We stripped out the complex Google Connector library entirely. Since we were on Cloud Run, we used the native **Unix Socket** (`/cloudsql/...`) directly with the standard `psycopg3` driver. Simple and bulletproof.

## 3. The "Port 8080" Cloud Run Timeout (UI Crash)
**The Problem:** The UI service kept returning `Error Code 9: container failed to start and listen on port 8080`.
**The Cause:** By default, Cloud Run expects all web apps to listen on port `8080`. However, Streamlit (our UI framework) hardcodes its server to listen on port `8501`. Cloud Run was knocking on 8080, getting no answer, and killing the app.
**The Fix:** In Terraform (`cloud_run.tf`), we added a `ports { container_port = 8501 }` block to explicitly tell Cloud Run where to look.

## 4. The LangGraph `NotImplementedError`
**The Problem:** `500 Internal Server Error` when asking a question. The logs showed `NotImplementedError` in `aget_tuple`.
**The Cause:** We were trying to execute the agent asynchronously (`await rag_agent.ainvoke()`), but we had attached a *Synchronous* database saver (`PostgresSaver`). 
**The Fix:** We switched the FastAPI endpoint to run synchronously (`rag_agent.invoke()`), properly aligning the execution flow with the database driver.

## 5. The LangGraph `UndefinedTable` Error
**The Problem:** Another `500 Internal Server Error` stating that the table "checkpoints" did not exist.
**The Cause:** When connecting to a brand new Cloud SQL database, the tables required by LangGraph to store conversation memory don't exist yet. 
**The Fix:** We added `checkpointer.setup()` to the initialization sequence in `graph.py`, telling LangGraph to auto-create its tables (`IF NOT EXISTS`) on startup.

## 6. The Logfire 500 Crash
**The Problem:** The app crashed randomly on startup with an "Authentication Required" error from Logfire.
**The Cause:** Locally, the developer was logged in via `logfire auth`. In the cloud container, there was no session. Because Logfire couldn't authenticate, it crashed the whole app.
**The Fix:** 
1. We wrapped `logfire.configure()` in a "Safety Shield" (`try-except`) so the app would survive even if observability failed.
2. We added the `LOGFIRE_TOKEN` to Terraform and injected it as an Environment Variable.

## 7. Eventarc 403 Permission Denied
**The Problem:** Terraform refused to create the Eventarc trigger, throwing a `storage.buckets.get permission denied` error.
**The Cause:** Google Cloud requires strict security handshakes. Cloud Storage didn't have permission to publish events, and Eventarc didn't have permission to look at Cloud Storage.
**The Fix:** In Terraform, we granted `roles/pubsub.publisher` to the Storage Service Account, and `roles/eventarc.serviceAgent` to the internal Eventarc agent, effectively unlocking the communication bridge.
