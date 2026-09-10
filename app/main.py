from fastapi import FastAPI
from api.documents import router as documents_router
from rag.retrieval import search_documents
from rag.generation import generate_answer


app = FastAPI(
    title="Enterprise Knowledge Intelligence System",
    description="AI-Powered Enterprise Knowledge Assistant",
    version="1.0.0"
)
app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "message": "Enterprise Knowledge Intelligence System is running smoothly"
    }


@app.get("/ask")
def ask_ai(question: str):

    # 1. Retrieve relevant documents
    results = search_documents(
        question,
        limit=7
    )

    # 2. Build context
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

    # 3. Generate answer
    answer = generate_answer(
        question,
        context
    )

    # 4. Build sources
    sources = []

    for result in results:

        sources.append({
            "document": result.payload["document_name"],
            "page": result.payload["page"],
            "score": result.score
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }