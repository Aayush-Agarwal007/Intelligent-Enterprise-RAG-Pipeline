from fastapi import APIRouter, UploadFile, File,HTTPException
from pathlib import Path
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

qdrant_client = QdrantClient(
    url="http://127.0.0.1:6333"
)
COLLECTION_NAME="enterprise_documents"
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
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
        status_code=400,
        detail="Only PDF files are supported"
    )

    # 1. Save uploaded file
    unique_filename=f"{uuid.uuid4()}_{file.filename}"
    file_path = DOCUMENTS_DIR / unique_filename

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
@router.get("/")
def list_documents():

    files = []

    for file_path in DOCUMENTS_DIR.iterdir():

        if file_path.is_file() and file_path.suffix.lower() == ".pdf":

            files.append({
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size
            })

    return {
        "total_documents": len(files),
        "documents": files
    }
    
@router.delete("/{filename}")
def delete_document(filename: str):

    file_path = DOCUMENTS_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete vectors from Qdrant
    qdrant_client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_name",
                    match=MatchValue(value=filename)
                )
            ]
        )
    )

    # Delete physical file
    file_path.unlink()

    return {
        "message": "Document deleted successfully",
        "filename": filename
    }