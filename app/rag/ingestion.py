import pymupdf
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from ollama import embed


QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION_NAME = "enterprise_documents"


qdrant_client = QdrantClient(
    url=QDRANT_URL
)


def load_pdf(file_path: str):

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text()

        if text.strip():

            pages.append({
                "page": page_number + 1,
                "text": text
            })

    document.close()

    return pages


def split_documents(pages):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(page["text"])

        for chunk in page_chunks:

            chunks.append({
                "text": chunk,
                "page": page["page"]
            })

    return chunks


def store_chunks_in_qdrant(chunks, document_name):
    document_id=str(uuid.uuid4())
    print("Chunks Received by Qdrant:", len(chunks))

    points = []

    for index, chunk in enumerate(chunks):

        response = embed(
            model="nomic-embed-text",
            input=chunk["text"]
        )

        embedding = response["embeddings"][0]

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk["text"],
                "document_name": document_name,
                "document_id": document_id,
                "page": chunk["page"],
                "chunk_id": index + 1
            }
        )
        print("Chunks received by Qdrant:", len(chunks))
        points.append(point)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)