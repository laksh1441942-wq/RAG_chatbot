from langchain_community.document_loaders import PyPDFLoader
from pdf2image import convert_from_path
from langchain_core.documents import Document
import pytesseract
import glob

pdf_files = glob.glob("data/*.pdf")

documents = []

for pdf_file in pdf_files:

    print(f"\nReading PDF: {pdf_file}")

    loader = PyPDFLoader(pdf_file)
    pdf_pages = loader.load()

    extracted_content = ""

    # Try normal text extraction
    for page in pdf_pages:
        extracted_content += page.page_content.strip()

    # If no text found → use OCR
    if not extracted_content:

        print("No normal text found.")
        print("Using OCR...\n")

        images = convert_from_path(pdf_file)

        text = ""

        for image in images:
            text += pytesseract.image_to_string(image)

        documents.append(
            Document(page_content=text)
        )

        print("OCR Extracted Text Preview:\n")
        print(text[:1000])

    else:

        documents.extend(pdf_pages)

        print("Normal Text Extracted Successfully.\n")

        print("Extracted Text Preview:\n")
        print(extracted_content[:1000])

    print("\n" + "="*80)