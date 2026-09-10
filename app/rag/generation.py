from ollama import chat


MODEL_NAME = "qwen2.5:3b"


def generate_answer(question: str, context: str):

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use information outside the context.
2. If the answer is not present in the context, say:
   "I could not find this information in the available documents."
3. Be concise and factual.
4. Do not make up information.

Context:
{context}

Question:
{question}

Answer:
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