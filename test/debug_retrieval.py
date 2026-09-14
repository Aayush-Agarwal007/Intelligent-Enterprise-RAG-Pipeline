from app.rag.retrieval import search_documents


question = "What are Aayush's programming languages?"

results = search_documents(
    question,
    limit=10
)

print("\n==============================")
print("QDRANT RESULTS")
print("==============================")

for i, result in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Score:", result.score)
    print("Document:", result.payload["document_name"])
    print("Page:", result.payload["page"])
    print("Text:")
    print(result.payload["text"][:500])