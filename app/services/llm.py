import vertexai
from vertexai.generative_models import GenerativeModel
from app.config import PROJECT_ID, LOCATION


model = GenerativeModel("gemini-2.5-flash")


def generate_answer(query, context):
    prompt = f"""
    Answer the question using the context below.
    If the contex is irrelevant , reply from your knowledge base

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    response = model.generate_content(prompt)
    return response.text