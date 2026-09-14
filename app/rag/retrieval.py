from qdrant_client import QdrantClient
from ollama import embed
from app.rag.reranker import rerank_documents

from app.rag.keyword_search import keyword_search


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


def normalize_scores(scores):

    if not scores:
        return []

    minimum = min(scores)
    maximum = max(scores)

    if maximum == minimum:
        return [1.0 for _ in scores]

    return [
        (score - minimum) / (maximum - minimum)
        for score in scores
    ]


def hybrid_search(question: str, limit: int = 7):

    # -------------------------
    # 1. Vector Search
    # -------------------------

    vector_results = search_documents(
        question,
        limit=limit
    )

    # -------------------------
    # 2. BM25 Search
    # -------------------------

    keyword_results = keyword_search(
        question,
        limit=limit
    )

    # -------------------------
    # 3. Get scores
    # -------------------------

    vector_scores = [
        float(result.score)
        for result in vector_results
    ]

    keyword_scores = [
        float(result["score"])
        for result in keyword_results
    ]

    # -------------------------
    # 4. Normalize scores
    # -------------------------

    normalized_vector_scores = normalize_scores(
        vector_scores
    )

    normalized_keyword_scores = normalize_scores(
        keyword_scores
    )

    # -------------------------
    # 5. Combine results
    # -------------------------

    combined = {}

    # Add vector results
    for result, score in zip(
        vector_results,
        normalized_vector_scores
    ):

        text = result.payload["text"]

        combined[text] = {
            "payload": result.payload,
            "vector_score": score,
            "keyword_score": 0.0
        }

    # Add BM25 results
    for result, score in zip(
        keyword_results,
        normalized_keyword_scores
    ):

        chunk = result["chunk"]
        text = chunk["text"]

        if text not in combined:

            combined[text] = {
                "payload": chunk,
                "vector_score": 0.0,
                "keyword_score": score
            }

        else:

            combined[text]["keyword_score"] = score

    # -------------------------
    # 6. Calculate hybrid score
    # -------------------------

    results = []

    for item in combined.values():

        hybrid_score = (
            0.6 * item["vector_score"]
            +
            0.4 * item["keyword_score"]
        )

        results.append({
            "payload": item["payload"],
            "score": hybrid_score
        })

    # -------------------------
    # 7. Sort
    # -------------------------

    results.sort(
    key=lambda x: x["score"],
    reverse=True
)

# Remove completely irrelevant results
    results = [
        result
        for result in results
        if result["score"] > 0
]

    return results[:limit]
def retrieve_with_reranking(question: str, limit: int = 5):

    # Get candidates from hybrid search
    hybrid_results = hybrid_search(
        question,
        limit=10
    )

    # Rerank the candidates
    reranked_results = rerank_documents(
        question,
        hybrid_results,
        limit=limit
    )

    return reranked_results