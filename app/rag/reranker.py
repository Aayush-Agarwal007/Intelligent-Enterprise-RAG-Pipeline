from sentence_transformers import CrossEncoder
from sympy import limit


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


reranker = CrossEncoder(
    MODEL_NAME
)


def rerank_documents(question: str, results: list, limit: int = 5):

    if not results:
        return []

    pairs = []

    for result in results:

        text = result["payload"]["text"]

        pairs.append(
            (question, text)
        )

    scores = reranker.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):

        reranked.append({
            "payload": result["payload"],
            "score": float(score)
        })

    reranked.sort(
    key=lambda x: x["score"],
    reverse=True
)

# Keep only reasonably relevant results
    reranked = [
        result
        for result in reranked
        if result["score"] > 0
]

    return reranked[:limit]