from unittest import result

from fastapi import FastAPI
from app.api.documents import router as documents_router
from app.rag.retrieval import hybrid_search, retrieve_with_reranking
from app.rag.generation import generate_answer
from app.rag.keyword_search import keyword_search
from app.rag.reranker import rerank_documents
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
    results = retrieve_with_reranking(
        question,
        limit=5
    )
    keyword_results = keyword_search(
    question,
    limit=7
)

    print("\nBM25 RESULTS:")
    for result in keyword_results:
        print(
        "Score:",
        result["score"],
        "| Document:",
        result["chunk"]["document_name"],
        "| Page:",
        result["chunk"]["page"]
    )

    # 2. Stop if no relevant document was found
    if not results:
        return {
            "question": question,
            "answer": "I could not find this information in the available documents.",
            "sources": []
        }

    # 3. Build context
    context_parts = []

    for result in results:

        payload = result["payload"]

        context_parts.append(
    f"""
Source: {payload["document_name"]}
Page: {payload["page"]}

{payload["text"]}
"""
)       

    context = "\n\n".join(context_parts)

    # 4. Generate answer
    answer = generate_answer(
        question,
        context
    )

    # 5. Build sources
    sources = []

    seen_sources = set()

    for result in results:
        payload = result["payload"]

        document = payload["document_name"]
        page = payload["page"]
        score = round(result["score"], 4)

        source_key = (document, page)

        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        sources.append({
            "document": document,
            "page": page,
            "score": score
    })
    return {
        "question": question,
        "answer": answer,
        "sources": sources
}