from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

    # Load Ollama model
llm = OllamaLLM(model="llama3")

def ask_question(query):

    db = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_function
    )

    # Retrieve relevant chunks
    results = db.similarity_search(query, k=8)

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

