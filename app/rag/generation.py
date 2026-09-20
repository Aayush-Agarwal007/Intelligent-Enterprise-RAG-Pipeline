from ollama import Client
ollama_client = Client(host="http://host.docker.internal:11434")

MODEL_NAME = "qwen2.5:3b"


def generate_answer(
    question: str,
    context: str,
    conversation_history: str = ""
):
    prompt = f"""
You are an enterprise knowledge assistant.

Your job is to answer the user's question using ONLY the information
provided in the CONTEXT below.

IMPORTANT RULES:

1. Treat the CONTEXT as your only source of truth.
2. Do not use your own general knowledge.
3. If the answer can be found anywhere in the CONTEXT, answer the question.
4. Do NOT say that the information is unavailable when relevant information
   exists in the CONTEXT.
5. If the answer genuinely cannot be found in the CONTEXT, respond exactly:
   "I could not find this information in the available documents."
6. Be concise and factual.
7. Do not provide source names, page numbers, or citations.

CONVERSATION HISTORY:
{conversation_history}
CONTEXT:
{context}



USER QUESTION:
{question}

ANSWER:
"""

    response = ollama_client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]
def rewrite_question(question: str, conversation_history: str):
    if not conversation_history.strip():
        return question

    prompt = f"""
Rewrite the user's latest question into a standalone search query.

Use the conversation history to resolve references such as:
- he
- she
- it
- that
- this
- previous project

Rules:
1. Preserve the user's original meaning.
2. Do not answer the question.
3. Do not add information that is not supported by the conversation.
4. Return only the rewritten question.
5. If the question is already standalone, return it unchanged.

CONVERSATION HISTORY:
{conversation_history}

LATEST USER QUESTION:
{question}

STANDALONE SEARCH QUERY:
"""

    response = ollama_client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()