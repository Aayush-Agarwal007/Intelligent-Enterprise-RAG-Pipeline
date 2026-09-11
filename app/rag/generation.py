from ollama import chat


MODEL_NAME = "qwen2.5:3b"


def generate_answer(question: str, context: str):

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
7. At the end, provide the source document and page number.
8. Never invent a document name or page number.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]