from fastapi import APIRouter, UploadFile, File
from pathlib import Path


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# Main project documents folder
DOCUMENTS_DIR = Path(__file__).resolve().parents[2] / "documents"

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    file_path = DOCUMENTS_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return {
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "path": str(file_path)
    }