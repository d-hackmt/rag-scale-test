import logfire
from langchain_groq import ChatGroq
from app.agents.state import AgentState
from app.services.core.config import settings
from app.services.cache.semantic_cache import check_cache, update_cache

# Global LLM holder for lazy init
_llm = None

def get_llm():
    """Lazy initialization of the Groq LLM."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.1
        )
    return _llm

def generate_node(state: AgentState):
    """
    Synthesizes a response using Documentation Context AND Conversation History.
    Now with Semantic Caching.
    """
    query = state["current_query"]
    user_msg = state["messages"][-1]["content"] if state["messages"] else ""
    
    # --- 🧠 STEP 1: CHECK SEMANTIC CACHE ---
    if settings.USE_SEMANTIC_CACHE:
        cached_response = check_cache(user_msg)
        if cached_response:
            return {
                "final_answer": cached_response,
                "status": "Response retrieved from Semantic Cache (✨ Fast)",
                "messages": [{"role": "assistant", "content": cached_response}]
            }

    # Format history for LLM
    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"
    
    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are a friendly and helpful Enterprise AI Assistant.
        Answer the user's latest message using the CONVERSATION HISTORY below.
        
        CONVERSATION HISTORY:
        {history_str}
        
        LATEST MESSAGE:
        "{user_msg}"
        """
    else:
        # Technical RAG Logic with Token Safety
        logfire.info("Generating technical RAG response.")
        max_context_chars = 25000 
        full_context = ""
        
        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
        You are a Senior Technical Architect. 
        Answer the question using the TECHNICAL CONTEXT provided. 
        
        TECHNICAL CONTEXT:
        {full_context}
        
        CONVERSATION HISTORY:
        {history_str}
        
        USER QUESTION:
        "{user_msg}"
        """
    
    with logfire.span("✍️ LLM Synthesis"):
        try:
            llm = get_llm()
            response = llm.invoke(prompt)
            
            # --- 💾 STEP 2: UPDATE CACHE ---
            if settings.USE_SEMANTIC_CACHE:
                update_cache(user_msg, response.content)
            
            logfire.info("Response synthesized successfully.")
            return {
                "final_answer": response.content,
                "status": "Response generated.",
                "messages": [{"role": "assistant", "content": response.content}]
            }
        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e
