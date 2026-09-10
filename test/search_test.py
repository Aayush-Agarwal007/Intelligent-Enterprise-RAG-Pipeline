from qdrant_client import QdrantClient
from ollama import embed
#connect ker lo Qdrant se 
client=QdrantClient(
    url="http://localhost:6333"
)
collection_name="enterprise_documents"
#user jo question puchega 
question="what is the name of Aayush College?"
#convert that question into embedding 
response=embed(
    model="nomic-embed-text",
    input=question
)
query_vector=response["embeddings"][0]
#search in Qdrant
result=client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=3
).points
print("Search results:")
for i, result in enumerate(result):
    print(f"Result {i + 1}:")
    print("ID:", result.id)
    print("Payload:", result.payload)
    print("Score:", result.score)
    print()