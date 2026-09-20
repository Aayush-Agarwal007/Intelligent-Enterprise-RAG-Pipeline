# from unittest import result
from app.rag.keyword_search import rebuild_bm25_index
# from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.db.database import get_messages,add_message,get_conversation
from app.db.database import (
    get_messages,
    add_message,
    create_conversation,
    update_conversation_title
)
from app.db.database import (
    get_messages,
    add_message,
    get_conversations,
    delete_conversation
)
from app.db.database import create_conversation
from app.api.documents import router as documents_router
from app.rag.retrieval import hybrid_search, retrieve_with_reranking
from app.rag.generation import generate_answer,rewrite_question 
from app.rag.keyword_search import keyword_search
from app.rag.reranker import rerank_documents
app = FastAPI(
    title="Enterprise Knowledge Intelligence System",
    description="AI-Powered Enterprise Knowledge Assistant",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup_event():
    rebuild_bm25_index()
    print("BM25 index rebuilt from PostgreSQL")
app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "message": "Enterprise Knowledge Intelligence System is running smoothly"
    }
@app.get("/conversations")
def list_conversations():
    conversations = get_conversations()

    return {
        "conversations": [
            {
                "id": conversation[0],
                "title": conversation[1],
                "created_at": conversation[2]
            }
            for conversation in conversations
        ]
    }  

@app.post("/conversations")
def create_new_conversation():
    conversation_id = create_conversation()

    return {
        "conversation_id": conversation_id,
        "title": "New Conversation"
    }
@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: int):

    messages = get_messages(conversation_id)

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": message[0],
                "role": message[1],
                "content": message[2],
                "created_at": message[3]
            }
            for message in messages
        ]
    }
@app.delete("/conversations/{conversation_id}")
def remove_conversation(conversation_id: int):

    deleted = delete_conversation(conversation_id)

    if deleted == 0:
        return {
            "message": "Conversation not found"
        }

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id
    }
@app.get("/ask")
def ask_ai(question: str, conversation_id: int):
        # Load previous conversation messages
    previous_messages = get_messages(conversation_id)
    conversation_history = "\n".join(
    f"{message[1]}: {message[2]}"
    for message in previous_messages
)

    print("\n========== CONVERSATION HISTORY ==========")

    for message in previous_messages:
        print(
            "Role:", message[1],
            "| Content:", message[2]
        )

    print("==========================================\n")

    # 1. Retrieve relevant documents
    # 1. Rewrite question using conversation history
    search_question = rewrite_question(
        question,
        conversation_history
)

    print("\nOriginal question:", question)
    print("Search question:", search_question)

# 2. Retrieve relevant documents
    results = retrieve_with_reranking(
        search_question,
        limit=10
)
    keyword_results = keyword_search(
    search_question,
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
    print("\n================ CONTEXT SENT TO LLM ================\n")
    print(context)
    print("\n=======================================================\n")
    # 4. Generate answer
    answer = generate_answer(
        question,
        context,
        conversation_history
    )
    # Save user question and AI answer
    add_message(
        conversation_id,
        "user",
        question
)

    add_message(
        conversation_id,
        "assistant",
        answer
)
    # Update conversation title using the first user question
    previous_user_messages = [
        message for message in previous_messages
        if message[1] == "user"
]

    if len(previous_user_messages) == 0:
        title = question.strip()

        if len(title) > 40:
            title = title[:40].rstrip() + "..."

        update_conversation_title(
            conversation_id,
            title
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