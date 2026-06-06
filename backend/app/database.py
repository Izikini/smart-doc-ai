import os

# Folder for storing text documents, avoiding dependency on the quirks of C++ vector DB libraries
DOCS_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", ".local_storage")
os.makedirs(DOCS_DATA_DIR, exist_ok=True)

def chunk_text(text: str, chunk_size: int = 600, chunk_overlap: int = 150) -> list[str]:
    """Chunk text into AI-friendly segments."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def save_document_to_vector_db(user_id: str, document_id: str, text: str):
    """
    Saves the document locally as a text file.
    This ensures that the original readable text never becomes binary garbage.
    """
    try:
        user_file = os.path.join(DOCS_DATA_DIR, f"doc_{user_id}.txt")
        with open(user_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Document successfully saved to local text storage for user {user_id}")
    except Exception as e:
        print(f"❌ Error saving document: {e}")
        raise e

def query_relevant_chunks(user_id: str, query: str, n_results: int = 3) -> str:
    """
    Finds the most relevant paragraphs in the document based on query keywords.
    Returns clean, original, and readable text for the AI.
    """
    try:
        user_file = os.path.join(DOCS_DATA_DIR, f"doc_{user_id}.txt")
        if not os.path.exists(user_file):
            return ""
            
        with open(user_file, "r", encoding="utf-8") as f:
            full_text = f.read()
            
        chunks = chunk_text(full_text)
        query_words = set(query.lower().split())
        
        # Score chunks by the number of keyword matches from the query
        scored_chunks = []
        for chunk in chunks:
            score = sum(1 for word in query_words if word in chunk.lower())
            scored_chunks.append((score, chunk))
            
        # Sort by descending relevance score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Take the top 3 best chunks of text
        top_chunks = [chunk for score, chunk in scored_chunks[:n_results]]
        return "\n\n---\n\n".join(top_chunks)
        
    except Exception as e:
        print(f"❌ Error querying text: {e}")
        return ""