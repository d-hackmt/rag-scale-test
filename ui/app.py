import streamlit as st
import requests

# 🔹 Your deployed API
API_URL = "https://rag-api-173472321372.us-central1.run.app/query"


st.set_page_config(page_title="RAG Chat", layout="wide")

st.title("📄 RAG PDF Assistant")

query = st.text_input("Ask a question from your documents:")

if st.button("Ask"):
    if query:
        with st.spinner("Thinking..."):
            try:
                response = requests.get(API_URL, params={"q": query})
                data = response.json()

                st.subheader("Answer")
                st.write(data.get("answer"))

                st.subheader("Context Used")
                for i, ctx in enumerate(data.get("context", [])):
                    st.write(f"Chunk {i+1}:")
                    st.write(ctx[:300] + "...")

            except Exception as e:
                st.error(f"Error: {e}")