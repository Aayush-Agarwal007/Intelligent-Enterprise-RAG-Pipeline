from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from ollama import embed

from document_loader import load_pdf, split_documents


# Connect to Qdrant
client = QdrantClient(
    url="http://127.0.0.1:6333"
)

collection_name = "enterprise_documents"


# Load PDF
pages = load_pdf("documents/RED_HAT.pdf")

# Split into chunks
chunks = split_documents(pages)

print("Total chunks:", len(chunks))


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
            "document_name": "RED_HAT.pdf",
            "page": chunk["page"],
            "chunk_id": index + 1
        }
    )

    points.append(point)

    print(f"Processed chunk {index + 1}/{len(chunks)}")


# Insert all chunks
client.upsert(
    collection_name=collection_name,
    points=points
)

print("\nAll chunks inserted successfully into Qdrant!")