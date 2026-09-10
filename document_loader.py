import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter


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


if __name__ == "__main__":

    pdf_path = "documents/RED_HAT.pdf"

    pages = load_pdf(pdf_path)

    print("Pages extracted:", len(pages))

    chunks = split_documents(pages)

    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i + 1} ---")
        print("Page:", chunk["page"])
        print(chunk["text"][:500])