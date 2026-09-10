from fastapi import FastAPI
from ollama import chat


app= FastAPI(
    title="Enterprise Knowledge Intelligence System",
    description="Ai-Powere enterprise knowledge assistant",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status":"Ok Aayush",
        "messgage":"Enterprise Knowledge Intelligence System is running smoothly"
    }
@app.get("/ask")
def ask_ai(question: str):
    response = chat(
        model="qwen2.5:3b",
        messages=[{
            "role":"user",
            "content":question
        }]
    )
    return {
        "question": question,
        "answer": response["message"]["content"]
    }