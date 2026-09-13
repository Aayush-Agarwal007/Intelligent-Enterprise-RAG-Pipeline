from rank_bm25 import BM25Okapi


# All chunks from uploaded documents
all_chunks = []

# BM25 index
bm25_index = None


def tokenize(text: str):
    return text.lower().split()


def add_chunks(chunks, document_name):
    global all_chunks
    global bm25_index

    for chunk in chunks:
        all_chunks.append({
            "text": chunk["text"],
            "page": chunk["page"],
            "document_name": document_name
        })

    tokenized_chunks = [
        tokenize(chunk["text"])
        for chunk in all_chunks
    ]

    bm25_index = BM25Okapi(tokenized_chunks)


def keyword_search(query: str, limit: int = 7):
    if bm25_index is None or not all_chunks:
        return []

    query_tokens = tokenize(query)

    scores = bm25_index.get_scores(query_tokens)

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indexes:

        score = float(scores[index])

        if score <= 0:
            continue

        results.append({
        "chunk": all_chunks[index],
        "score": score
    })

        if len(results) >= limit:
            break

    return results