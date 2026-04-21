from vertexai.language_models import TextEmbeddingModel

model = None
BATCH_SIZE = 50  # Reduced from 200 to stay within 20,000 token limit per request

def get_embedding_model():
    global model
    if model is None:
        model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    return model


def embed_texts(texts):
    model = get_embedding_model()
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        response = model.get_embeddings(batch)

        batch_embeddings = [e.values for e in response]
        all_embeddings.extend(batch_embeddings)

        print(f"Processed batch {i} → {i+len(batch)}")

    return all_embeddings