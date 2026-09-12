import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.rag.keyword_search import (
    build_bm25_index,
    keyword_search
)


chunks = [
    {
        "text": "Employees must submit leave requests through the HR portal.",
        "page": 1
    },
    {
        "text": "Employees can work remotely after receiving manager approval.",
        "page": 2
    },
    {
        "text": "The company provides health insurance and retirement benefits.",
        "page": 3
    },
    {
        "text": "Employees must follow the company's security policy.",
        "page": 4
    }
]


# Build BM25 index
bm25 = build_bm25_index(chunks)


# Search
results = keyword_search(
    bm25,
    chunks,
    "employee security policy",
    limit=3
)

print("\nBM25 SEARCH RESULTS\n")

for result in results:
    print("Score:", result["score"])
    print("Page:", result["chunk"]["page"])
    print("Text:", result["chunk"]["text"])
    print("-" * 60)