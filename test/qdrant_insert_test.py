from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from ollama import embed


QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION_NAME = "enterprise_documents"

qdrant_client = QdrantClient(
    url="http://127.0.0.1:6333"
)


def store_chunks_in_qdrant(chunks, document_name):

    points = []

    for index, chunk in enumerate(chunks):

        # Generate embedding
        response = embed(
            model="nomic-embed-text",
            input=chunk["text"]
        )

        embedding = response["embeddings"][0]

        # Create Qdrant point
        point = PointStruct(
            id=index + 1,
            vector=embedding,
            payload={
                "text": chunk["text"],
                "document_name": document_name,
                "page": chunk["page"],
                "chunk_id": index + 1
            }
        )

        points.append(point)

    # Insert into Qdrant
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)