from fastapi import FastAPI
from ollama import chat, embed
from qdrant_client import QdrantClient


app = FastAPI(
    title="Enterprise Knowledge Intelligence System",
    description="AI-Powered Enterprise Knowledge Assistant",
    version="1.0.0"
)


# Qdrant connection
qdrant_client = QdrantClient(
    url="http://127.0.0.1:6333"
)

COLLECTION_NAME = "enterprise_documents"


@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "message": "Enterprise Knowledge Intelligence System is running smoothly"
    }


@app.get("/ask")
def ask_ai(question: str):

    # 1. Convert question into embedding
    embedding_response = embed(
        model="nomic-embed-text",
        input=question
    )

    query_vector = embedding_response["embeddings"][0]


    # 2. Search Qdrant
    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=7
    ).points


    # 3. Build context
    context_parts = []

    for result in results:

        context_parts.append(
            f"""
Source: {result.payload["document_name"]}
Page: {result.payload["page"]}

{result.payload["text"]}
"""
        )

    context = "\n\n".join(context_parts)


    # 4. Ask Qwen
    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:

"I could not find this information in the available documents."

Be concise and factual.

Context:

{context}

Question:

{question}

Answer:
"""


    llm_response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    answer = llm_response["message"]["content"]


    # 5. Build sources
    sources = []

    for result in results:

        sources.append({
            "document": result.payload["document_name"],
            "page": result.payload["page"],
            "score": result.score
        })


    # 6. Return response
    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }