from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from rag.ingestion import (
    load_pdf,
    split_documents,
    store_chunks_in_qdrant
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "documents"
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    # 1. Save uploaded file
    file_path = DOCUMENTS_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # 2. Extract PDF text
    pages = load_pdf(str(file_path))

    # 3. Split text into chunks
    chunks = split_documents(pages)

    # 4. Store chunks in Qdrant
    stored_chunks = store_chunks_in_qdrant(
        chunks,
        file.filename
    )
    return {
    "message": "Document processed and indexed successfully",
    "filename": file.filename,
    "pages": len(pages),
    "chunks": len(chunks),
    "indexed_chunks": stored_chunks
}