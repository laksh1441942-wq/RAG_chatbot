from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
import os
from dotenv import load_dotenv

load_dotenv()

llm = OllamaLLM(model=os.getenv('OLLAMA_MODEL','llama3'))

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

chroma_db_path = os.getenv('CHROMA_DB_PATH', 'chroma_db')

db = Chroma(
        persist_directory=chroma_db_path,
        embedding_function=embedding_function
    )

def ask_question(query):

    # Retrieve relevant chunks
    retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 8, "fetch_k": 30}
)

    results = retriever.invoke(query)

    print("\n========== RETRIEVED DOCS ==========\n")

    for doc in results:
        print(doc.metadata)
        print(doc.page_content[:200])
        print("----------------------------------")

    sources=[]
    for doc in results:
        source = doc.metadata.get("source","Unknown")
        page = doc.metadata.get("page_label", 0)
        filename=os.path.basename(source)
        sources.append(f"{filename} (Page {page})")
    sources=list(set(sources))
    sources = sources[:3]



    # Combine retrieved chunks
    context = "\n\n".join(
        [result.page_content for result in results]
    )

    # Create prompt
    prompt = f"""
    You are a RAG assistant.

    Answer ONLY from the provided context.

    Rules:
    1. Give short direct answers for factual questions.
    2. Use at most 1-2 sentences unless the user asks for details.
    3. You may make simple logical inferences from the context.
    4. Do not explain your reasoning unless asked.
    5. If the answer is not in the context, respond exactly:

    I could not find this information in the uploaded documents.

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    # Generate answer
    response = llm.invoke(prompt)

    print("\n========== CONTEXT ==========\n")
    print(context[:3000])
    print("\n=============================\n")
    
    return {
        "answer": response,
        "sources": sources
    }

