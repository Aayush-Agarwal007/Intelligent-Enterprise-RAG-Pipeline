from qdrant_client import QdrantClient
from ollama import embed,chat
client=QdrantClient(
    url="http://localhost:6333"
)
collection_name="enterprise_documents"
question="Highest education of Aayush?"
response=embed(
    model="nomic-embed-text",
    input=question
)
query_vector=response["embeddings"][0]
results=client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=7
).points
print("\n==============================")
print("RETRIEVED CHUNKS")
print("==============================")

for i, result in enumerate(results):
    print(f"\n--- Result {i + 1} ---")
    print("Score:", result.score)
    print("Page:", result.payload["page"])
    print("Text:")
    print(result.payload["text"])
context= "\n\n".join(
    result.payload["text"]
    for result in results
)
prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I could not find this information in the available documents."

Context:
{context}

Question:
{question}

Answer:
"""
response = chat(
    model="qwen2.5:3b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
# 6. Display answer
print("\n==============================")
print("QUESTION")
print("==============================")
print(question)

print("\n==============================")
print("ANSWER")
print("==============================")
print(response["message"]["content"])