import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 💡 Locate the absolute path to the .env file one level above the app folder
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load the .env file from the absolute path
load_dotenv(dotenv_path=ENV_PATH)

# Add a strict check: if the key is missing in the environment, fail with a clear error
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        f"\n[ERROR] Critical issue: environment variable 'OPENAI_API_KEY' not found!\n"
        f"Make sure the file '.env' exists at: {ENV_PATH}\n"
        f"And contains a line like: OPENAI_API_KEY=sk-proj-..."
    )

# Import AI and database services ONLY after successful environment key validation
from app.ai_service import extract_structured_data, ask_llm_with_context
from app.database import save_document_to_vector_db

app = FastAPI(title="Smart-Doc AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    question: str

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Smart-Doc AI API is running successfully!"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = Form(...)):
    if not file.filename.endswith(('.txt', '.pdf')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Only .txt and .pdf are allowed.")
    try:
        contents = await file.read()
        document_text = contents.decode("utf-8", errors="ignore")
        if not document_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        
        document_id = str(uuid.uuid4())
        extracted_json = extract_structured_data(document_text)
        save_document_to_vector_db(user_id=user_id, document_id=document_id, text=document_text)
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "user_id": user_id,
            "extracted_data": extracted_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.post("/api/chat")
def chat_with_document(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    ai_response = ask_llm_with_context(user_id=request.user_id, question=request.question)
    return {
        "user_id": request.user_id,
        "question": request.question,
        "response": ai_response
    }