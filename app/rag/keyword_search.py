from rank_bm25 import BM25Okapi
def tokenize(text: str):
    return text.lower().split()
def build_bm25_index(chunks):
    """
    Build a BM25 index from document chunks.
    """
    tokenized_chunks=[
        tokenize(chunk["text"])
        for chunk in chunks
    ]
    bm25=BM25Okapi(tokenized_chunks)
    return bm25
def keyword_search(bm25,chunks,query:str,limit:int=7):
    """
    Perform a keyword search using the BM25 index.
    """
    query_tokens=tokenize(query)
    scores=bm25.get_scores(query_tokens)
    ranked_indexes=sorted(
        range(len(scores)),
        key=lambda i:scores[i],
        reverse=True
            )
    results=[]
    for idx in ranked_indexes[:limit]:
        results.append({
            "chunk":chunks[idx],
        "score":float(scores[idx])
        })
        return results