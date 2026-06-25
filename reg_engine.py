from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model=os.getenv("NEX_AGI_MODEL", "Nex-N2-Pro"),
                 api_key=os.getenv("LLM_API_KEY"),
                 base_url=os.getenv("NEX_AGI_BASE_URL"),
                 temperature=0)

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

chroma_db_path = os.getenv('CHROMA_DB_PATH', 'chroma_db')

db = Chroma(
        persist_directory=chroma_db_path,
        embedding_function=embedding_function
    )

def ask_question(query):

    # Retrieve relevant chunks - optimized for accuracy
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 25}
    )

    results = retriever.invoke(query)

    # Only extract sources from top 2 most relevant chunks
    top_results = results[:2]
    
    sources = []
    for doc in top_results:
        source = doc.metadata.get("source","Unknown")
        page = doc.metadata.get("page_label") or doc.metadata.get("page")
        filename=os.path.basename(source)
        
        # Only add page number if it exists and is not None
        if page is not None:
            source_str = f"{filename} (Page {page})"
        else:
            source_str = filename
            
        if source_str not in sources:
            sources.append(source_str)



    # Combine retrieved chunks
    context = "\n\n".join(
        [result.page_content for result in results]
    )

    # Create prompt with clear instructions
    prompt = f"""You are a RAG assistant. Your job is to
      answer questions ONLY from the provided context.

RULES (Follow strictly):
1. Answer ONLY from the provided context - do not use external knowledge
2. If the answer is not in the context, respond: "I could not find this information in the uploaded documents."
3. For factual questions: Give short, direct answers (1-2 sentences max)
4. For complex questions: Provide more detail only if the context supports it
5. DO NOT mention the document names or sources in your answer - they will be shown separately
6. Do not explain your reasoning unless asked

CONTEXT:
{context}

    QUESTION: {query}

    ANSWER:"""

    # Generate answer
    response = llm.invoke(prompt)
    
    answer = response.content if hasattr(response, "content") else response

    return {
        "answer": answer,
        "sources": sources
    }

