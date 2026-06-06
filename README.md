# Smart-Doc AI 🚀

Smart-Doc AI is a fully local, privacy-first document analysis and RAG (Retrieval-Augmented Generation) platform. The application allows you to upload text documents such as contracts, invoices, and technical specifications, automatically extracts key operational data into a clean table, and provides an interactive chat interface for searching information within the uploaded file.

The entire AI pipeline runs 100% locally on your machine using Ollama and the Llama 3 model. This ensures maximum data security (files are not sent to external servers) and zero API costs.

---

## 🏗️ Architecture and Technology Stack

- **Frontend:** React, Vite, TailwindCSS (modern, responsive UI with dark mode support).
- **Backend:** FastAPI (Python 3.14), Uvicorn, Pydantic v2 (strict input validation).
- **Local AI Engine:** Ollama running the `llama3` model.
- **RAG System:** Custom, stable chunk-indexing and keyword-based search designed to avoid native C++ vector DB dependencies and run reliably on Python 3.14+.

---

## 🛠️ Prerequisites

Before running the project, make sure you have:
1. Node.js 18 or newer and npm.
2. Python 3.10–3.14.
3. Ollama installed locally.

### Local model setup
1. Install Ollama from https://ollama.com.
2. Download and run the Llama 3 model locally:

```bash
ollama run llama3
```

Keep this terminal open while the model is active.

---

## 🚀 Project Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env        # Edit .env and set required values
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

The backend API will be available at: http://127.0.0.1:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the provided local URL (typically http://localhost:5173/) in your browser.

---

## 📊 Manual Testing

Create a file named `test_en.txt` with the following content and upload it through the UI:

```
DOCUMENT TYPE: COMMERCIAL INVOICE
INVOICE NUMBER: INV-2026-8891
ISSUE DATE: May 15, 2026

PRIMARY PROVIDER:
NeuroNets & Code LLC

PRIMARY CLIENT:
Bogdan Enterprises (Represented by: Mr. Bogdan)

TOTAL AMOUNT DUE: 4500.00 USD
TAX STATUS: VAT 0% (Tax Exempt)

PAYMENT TERMS AND DEADLINES:
Full payment must be processed via bank transfer within 5 business days from the issue date.
```

Click the "Analyze with AI" button in the UI. The local model should extract the document fields and populate the table with Type, Client, Date, and Amount. Then use the chat interface to ask:

- Who is the primary client listed?
- What is the total amount due?
- How many days does the client have to pay?

---

## 🧪 Automated Integration Tests

The backend includes integration tests that simulate frontend usage: uploading sample files to FastAPI, validating AI-generated JSON, and verifying the RAG workflow.

Install the test tools if needed:

```bash
pip install pytest httpx
```

Run tests from the `backend` directory:

```bash
PYTHONPATH=. pytest -v test_main.py
```

These tests verify endpoint behavior, extraction of the sample invoice amount, and chat response accuracy.

---

## 🛡️ Reliability and Performance

- **Fallback validation:** Pydantic safeguards replace missing values with safe defaults so the backend does not fail on imperfect model output.
- **Local keyword search:** Document text is indexed by keyword chunks, providing clean context to the model.
- **Stable results:** Low temperature settings help keep responses factual and reduce hallucinations..
