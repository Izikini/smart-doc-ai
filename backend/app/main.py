import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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