import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Создаем тестового клиента FastAPI
client = TestClient(app)

# Пути к нашим проверочным файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVOICE_PATH = os.path.join(BASE_DIR, "tests_data", "invoice.txt")
CONTRACT_PATH = os.path.join(BASE_DIR, "tests_data", "contract.txt")

TEST_USER_ID = "test_user_123"

def test_root_endpoint():
    """Проверяем, что бэкенд вообще живой"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_invoice_upload_and_extraction():
    """Тест: Загрузка инвойса и проверка локального извлечения данных через Llama 3"""
    assert os.path.exists(INVOICE_PATH), "Файл invoice.txt не найден в tests_data!"
    
    with open(INVOICE_PATH, "rb") as file:
        response = client.post(
            "/api/upload",
            files={"file": ("invoice.txt", file, "text/plain")},
            data={"user_id": TEST_USER_ID}
        )
        
    assert response.status_code == 200
    data = response.json()
    
    # Проверяем структуру ответа бэкенда
    assert "extracted_data" in data
    extracted = data["extracted_data"]
    
    # Локальный ИИ должен вытащить данные (проверяем, что это не дефолтный Parsing Error)
    assert extracted["document_type"] != "Parsing Error"
    assert extracted["total_amount"] == 4500.00
    assert "Bogdan" in extracted["client_name"]


def test_contract_upload_and_rag_chat():
    """Тест: Загрузка контракта, сохранение в базу данных и проверка RAG-чата"""
    assert os.path.exists(CONTRACT_PATH), "Файл contract.txt не найден в tests_data!"
    
    # 1. Сначала загружаем контракт, чтобы он проиндексировался в локальном хранилище
    with open(CONTRACT_PATH, "rb") as file:
        upload_resp = client.post(
            "/api/upload",
            files={"file": ("contract.txt", file, "text/plain")},
            data={"user_id": TEST_USER_ID}
        )
    assert upload_resp.status_code == 200
    
    # 2. Задаем каверзный вопрос в чат по этому документу
    chat_payload = {
        "user_id": TEST_USER_ID,
        "question": "What is the mandatory core hours for live collaboration?"
    }
    
    chat_resp = client.post("/api/chat", json=chat_payload)
    assert chat_resp.status_code == 200
    
    chat_data = chat_resp.json()
    assert "response" in chat_data
    
    ai_answer = chat_data["response"].lower()
    
    # Локальная Llama 3 должна найти ответ в тексте, который мы подсунули
    assert "11" in ai_answer or "3" in ai_answer or "cet" in ai_answer