from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

response = llm.invoke(
    "Explain Retrieval-Augmented Generation (RAG) in AI in simple words"
)

print(response)