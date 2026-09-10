import fitz
pdf_path="documents/RED_HAT.pdf"
document = fitz.open(pdf_path)
print("Number of pages in the PDF:", document.page_count)
print("Metadata of the PDF:", document.metadata)
for page_number, page in enumerate(document):
    text = page.get_text()
    print(f"Text from page {page_number + 1}:\n{text}\n")
    print(text[:1000])
document.close()