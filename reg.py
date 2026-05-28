from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from pdf2image import convert_from_path
from langchain_core.documents import Document
import glob, pytesseract
import os
import shutil


# Load PDFs
documents= []
pdf_files =glob.glob("data/*.pdf")

for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    pdf_pages=loader.load()
    extracted_content=""
    for page in pdf_pages:
        extracted_content += page.page_content.strip()
    if  not extracted_content:
        images =convert_from_path(pdf_file)
        text =""
        for page in images:
            text+=pytesseract.image_to_string(page)
        documents.append(Document(page_content=text))
    else:
        documents.extend(pdf_pages)


# Split text into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

# Embedding model
embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

if os.path.exists("chroma_db"):

    if os.path.isdir("chroma_db"):
        shutil.rmtree("chroma_db")

    print("Loading Existing Database...")
    db = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_function
    )
else:
    print("Creating New Database...")
    db = Chroma.from_documents(
    chunks,
    embedding_function,
    persist_directory="chroma_db")


    # Load Ollama model
llm = OllamaLLM(model="llama3")

def ask_question(query):

    # Retrieve relevant chunks
    results = db.similarity_search(query, k=3)

    # Combine retrieved chunks
    context = "\n\n".join(
        [result.page_content for result in results]
    )

    # Create prompt
    prompt = f"""
    Answer the question using only the provided context.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    # Generate answer
    response = llm.invoke(prompt)

    return response

