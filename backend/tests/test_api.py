from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Smart-Doc AI API is running successfully!"}

def test_upload_wrong_file_type():
    files = {"file": ("test.png", b"fake image content", "image/png")}
    data = {"user_id": "test_user"}
    response = client.post("/api/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Only .txt and .pdf are allowed" in response.json()["detail"]

def test_chat_empty_question():
    payload = {"user_id": "test_user", "question": "   "}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 400
    assert "Question cannot be empty" in response.json()["detail"]