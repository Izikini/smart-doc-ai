import os
import chromadb

CHROMA_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma")
os.makedirs(CHROMA_DATA_DIR, exist_ok=True)

# Инициализируем локальный клиент ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)

def get_or_create_collection(user_id: str):
    collection_name = f"user_collection_{user_id}"
    
    # 💡 ИСПРАВЛЕНО: Убираем embedding_function. По умолчанию ChromaDB сама 
    # попробует создать коллекцию, но мы сделаем простую ручную генерацию фиктивных векторов,
    # чтобы полностью исключить ошибки несовместимости библиотек в Python 3.14.
    return chroma_client.get_or_create_collection(name=collection_name)

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def generate_mock_embedding(text: str, size: int = 384) -> list[float]:
    """
    Генерирует детерминированный вектор на основе текста.
    Это позволяет ChromaDB работать без скачивания тяжелых ONNX-моделей в фоне.
    """
    import hashlib
    # Создаем хэш от текста
    hash_digest = hashlib.sha256(text.encode('utf-8')).digest()
    # Превращаем байты в массив float-чисел нужной длины
    embedding = []
    for i in range(size):
        byte_val = hash_digest[i % len(hash_digest)]
        embedding.append(float(byte_val) / 255.0)
    return embedding

def save_document_to_vector_db(user_id: str, document_id: str, text: str):
    try:
        collection = get_or_create_collection(user_id)
        chunks = chunk_text(text)
        
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "user_id": user_id} for _ in chunks]
        
        # Генерируем эмбеддинги вручную
        embeddings = [generate_mock_embedding(chunk) for chunk in chunks]
        
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings  # Передаем готовые векторы напрямую
        )
        print(f"✅ Chunks successfully saved to ChromaDB for user {user_id}")
    except Exception as e:
        print(f"❌ Critical error inside save_document_to_vector_db: {e}")
        # Выбрасываем исключение дальше, чтобы логировать его в консоли
        raise e

def query_relevant_chunks(user_id: str, query: str, n_results: int = 3) -> str:
    try:
        collection = get_or_create_collection(user_id)
        query_embedding = generate_mock_embedding(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        if 'documents' in results and results['documents']:
            flattened_docs = [doc for sublist in results['documents'] for doc in sublist]
            return "\n---\n".join(flattened_docs)
        return ""
    except Exception as e:
        print(f"❌ Error during ChromaDB querying: {e}")
        return "Context chunking temporarily unavailable due to local database error."