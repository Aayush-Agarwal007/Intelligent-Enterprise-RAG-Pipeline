from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from ollama import embed
client=QdrantClient(
    url="http://localhost:6333"
)
response =embed(
    model="nomic-embed-text",
    input="Hii Aayush Padh Rha hai"
)
embedding= response["embeddings"][0]
vector_size=len(embedding)
print("embedding dimensions:", vector_size)
collection_name="Enterprise collection"
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
)
print(f"collection '{collection_name}' created successfully")
print(client.get_collections())