# Smart-Doc AI — Multi-tenant Document Analyzer & RAG Platform

An advanced full-stack application that processes unstructured documents (PDF/TXT), extracts strictly validated JSON entities, and indexes text representations into a vector database for semantic context-aware chat.

## 🚀 Technical Stack
- **Frontend:** React (Hooks, Functional Components), Vite, Lucide Icons, Vanilla CSS3 (Flexbox/Grid).
- **Backend:** Python, FastAPI (Asynchronous endpoints, Multipart form parsing), Pydantic v2 (Strict type matching).
- **AI Integration:** OpenAI API (`gpt-4o-mini` for JSON parsed mode, `text-embedding-3-small` for semantic tokens).
- **Database:** ChromaDB (Vector store, multi-tenant separate user spaces).
- **Testing:** PyTest (API client logic verification).

## 📦 Project Setup

### Backend
1. Go to backend directory: `cd backend`
2. Create and activate environment: `python3 -m venv venv && source venv/bin/activate`
3. Install requirements: `pip install -r requirements.txt`
4. Copy environment variables: `cp .env.example .env` (and fill in your real `OPENAI_API_KEY`)
5. Run server: `PYTHONPATH=. uvicorn app.main:app --reload`

### Frontend
1. Go to frontend directory: `cd frontend`
2. Install packages: `npm install`
3. Start development environment: `npm run dev`

### Running Tests
To ensure endpoint validity, run: `pytest` inside the backend folder.