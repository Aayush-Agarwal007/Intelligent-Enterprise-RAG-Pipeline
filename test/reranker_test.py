import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.rag.reranker import rerank_documents


question = "What is Aayush's highest education?"


results = [
    {
        "payload": {
            "text": "Aayush completed his B.Tech degree in Computer Science.",
            "document_name": "DEC_Developer.pdf",
            "page": 1
        },
        "score": 0.7
    },
    {
        "payload": {
            "text": "Aayush has solved more than 400 problems on LeetCode.",
            "document_name": "DEC_Developer.pdf",
            "page": 1
        },
        "score": 0.6
    },
    {
        "payload": {
            "text": "Aayush has experience building production RAG systems.",
            "document_name": "DEC_Developer.pdf",
            "page": 1
        },
        "score": 0.5
    },
    {
        "payload": {
            "text": "The company uses AWS for cloud infrastructure.",
            "document_name": "Amazon.pdf",
            "page": 1
        },
        "score": 0.4
    }
]


reranked_results = rerank_documents(
    question,
    results,
    limit=4
)


print("\nRERANKED RESULTS\n")

for result in reranked_results:

    print("Score:", result["score"])
    print("Document:", result["payload"]["document_name"])
    print("Page:", result["payload"]["page"])
    print("Text:", result["payload"]["text"])
    print("-" * 60)