import streamlit as st
import requests
import time

# 🔹 Configuration
API_URL = "https://rag-api-173472321372.us-central1.run.app/query"

st.set_page_config(
    page_title="Enterprise RAG",
    page_icon="🤖",
    layout="centered", # Centered layout feels more premium and focused
)

# Sidebar for System Status
with st.sidebar:
    st.title("🤖 System Status")
    st.success("API: Online")
    st.divider()
    st.markdown("**Infrastructure**")
    st.info("LLM: Groq Llama 3.3\n\nVector: Qdrant\n\nRanker: Vertex AI")
    st.divider()
    st.caption("Enterprise Agentic RAG v2.0")

st.title("Enterprise Agentic RAG")
st.caption("High-performance vector search with semantic re-ranking")

# Use a clean container for the chat interaction
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message:
            with st.expander("🔍 Context & Sources"):
                st.write(message["data"].get("answer")) # Fallback
                st.json(message["data"])

# Chat Input
if prompt := st.chat_input("Ask me anything about the documents..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        # Use st.status for a very clean "Agent is working" look
        with st.status("Agent Orchestration...", expanded=True) as status:
            st.write("Searching Qdrant Vector Store...")
            start_time = time.time()
            
            try:
                response = requests.get(API_URL, params={"q": prompt}, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    st.write("Performing Semantic Re-ranking...")
                    st.write("Finalizing Reasoning...")
                    status.update(label=f"Completed in {time.time()-start_time:.1f}s", state="complete", expanded=False)
                    
                    # Main Answer
                    st.markdown(data.get("answer"))
                    
                    # Reasoning Section
                    if data.get("reasoning"):
                        with st.expander("🤔 Agent Reasoning"):
                            st.info(data.get("reasoning"))
                    
                    # Sources Section
                    if data.get("sources"):
                        with st.expander("🔗 Technical Sources"):
                            for src in data.get("sources"):
                                st.markdown(f"- {src}")
                    
                    # Tool History
                    if data.get("tool_history"):
                        with st.expander("🛠 Tool Execution Log"):
                            st.table(data.get("tool_history"))

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": data.get("answer"),
                        "data": data
                    })
                else:
                    status.update(label="API Error", state="error")
                    st.error(f"Error {response.status_code}: {response.text}")
            
            except Exception as e:
                status.update(label="Connection Failed", state="error")
                st.error(f"Failed to connect to backend: {e}")