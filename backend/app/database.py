import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
os.makedirs(CHROMA_DATA_DIR, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

def get_or_create_collection(user_id: str):
    collection_name = f"user_collection_{user_id}"
    return chroma_client.get_or_create_collection(
        name=collection_name, 
        embedding_function=openai_ef
    )

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def save_document_to_vector_db(user_id: str, document_id: str, text: str):
    collection = get_or_create_collection(user_id)
    chunks = chunk_text(text)
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "user_id": user_id} for _ in chunks]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)

def query_relevant_chunks(user_id: str, query: str, n_results: int = 3) -> str:
    collection = get_or_create_collection(user_id)
    results = collection.query(query_texts=[query], n_results=n_results)
    flattened_docs = [doc for sublist in results['documents'] for doc in sublist]
    return "\n---\n".join(flattened_docs)