import glob
import os
import shutil
import sys

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from pdf2image import convert_from_path
import pytesseract
from dotenv import load_dotenv

load_dotenv()

# Embedding model
embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

chroma_db_path = os.getenv("CHROMA_DB_PATH", 'chroma_db')

# Only delete if we're processing multiple PDFs, otherwise append new documents
documents = []
pdf_path = sys.argv[1]
pdf_files = glob.glob(pdf_path)

# Load existing database or create new one
try:
    db = Chroma(
        persist_directory=chroma_db_path,
        embedding_function=embedding_function
    )
    print(f"Loaded existing database from {chroma_db_path}")
except:
    print(f"Creating new database at {chroma_db_path}")
    db = None

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

print("Loaded PDFs:")
for pdf_file in pdf_files:
    print(pdf_file)
print(f"Documents loaded: {len(documents)}")

# Split text into chunks - smaller, more focused chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(documents)

print(f"Total Chunks Created: {len(chunks)}")

for chunk in chunks:
    chunk.metadata["source"] = pdf_file

# Add or create database
if db is None:
    db = Chroma.from_documents(
        chunks,
        embedding_function,
        persist_directory=chroma_db_path
    )
    print("Created new database successfully!")
else:
    # Append new documents to existing database
    db.add_documents(chunks)
    print(f"Added {len(chunks)} new chunks to existing database!")