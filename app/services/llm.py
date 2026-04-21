from vertexai.generative_models import GenerativeModel
_model = None

def get_model():
    global _model
    if _model is None:
        _model = GenerativeModel("gemini-2.5-flash") # Fixed model name to a known valid one
    return _model


def generate_answer(query, context):
    model = get_model()

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