from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
db = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding_function
    )

    # Load Ollama model
llm = OllamaLLM(model="llama3")

def ask_question(query):

    # Retrieve relevant chunks
    results = db.similarity_search(query, k=8)

    # Combine retrieved chunks
    context = "\n\n".join(
        [result.page_content for result in results]
    )

    # Create prompt
    prompt = f"""
    You are a helpful assistant.

    Use ONLY the provided context.

    If the answer is not found in the context,
    say:

    "I could not find this information in the uploaded documents."

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    # Generate answer
    response = llm.invoke(prompt)
    


    return response

