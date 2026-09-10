from ollama import embed
from document_loader import load_pdf, split_documents


pdf_path = "documents/RED_HAT.pdf"

# Load PDF
pages = load_pdf(pdf_path)

# Split into chunks
chunks = split_documents(pages)

print("Total chunks:", len(chunks))


# Generate embedding for the first chunk
text = chunks[0]["text"]

response = embed(
    model="nomic-embed-text",
    input=text
)

embedding = response["embeddings"][0]

print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First 10 values:", embedding[:10])