import glob
import os
import shutil

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from pdf2image import convert_from_path
import pytesseract

# Embedding model
embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

if os.path.exists("chroma_db"):

    shutil.rmtree("chroma_db")

documents= []
pdf_files =glob.glob("data/*.pdf")

for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    pdf_pages=loader.load()
    extracted_content=""
    for page in pdf_pages:
        extracted_content += page.page_content.strip()
    if not extracted_content:
        images =convert_from_path(pdf_file)
        text =""
        for page in images:
            text+=pytesseract.image_to_string(page)
        documents.append(Document(page_content=text))
    else:
        documents.extend(pdf_pages)

for doc in documents:
    print(doc.metadata)


# Split text into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

print(f"Total Chunks Created: {len(chunks)}")

db=Chroma.from_documents(
    chunks,
    embedding_function,
    persist_directory="chroma_db"
)


print("Database Created Successfully!")