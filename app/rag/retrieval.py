from qdrant_client import QdrantClient
from ollama import embed
qdrant_client = QdrantClient(
    url="http://127.0.0.1:6333"
)

COLLECTION_NAME = "enterprise_documents"

def search_documents(question: str, limit: int = 7):

    # Convert question into embedding
    response = embed(
        model="nomic-embed-text",
        input=question
    )

    query_vector = response["embeddings"][0]

    # Search Qdrant
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        score_threshold=0.6
    ).points

    return results