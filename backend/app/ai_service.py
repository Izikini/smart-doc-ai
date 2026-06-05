import os
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ExtractedDocumentData(BaseModel):
    document_type: str = Field(description="Type of the document, e.g., Invoice, Contract, Resume, Receipt")
    client_name: str = Field(description="Name of the person or company mentioned as the primary actor/client")
    date: str = Field(description="Key date found in the document (YYYY-MM-DD format if possible)")
    total_amount: float = Field(description="Total monetary value or amount mentioned, 0.0 if not applicable")
    summary: str = Field(description="A brief 2-sentence summary of the document's content")

def extract_structured_data(document_text: str) -> ExtractedDocumentData:
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert AI data extraction assistant. Analyze the unstructured document text and extract structured fields according to the provided schema."},
                {"role": "user", "content": f"Please extract data from this document content:\n\n{document_text}"}
            ],
            response_format=ExtractedDocumentData,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"Error during AI data extraction: {e}")
        return ExtractedDocumentData(document_type="Unknown", client_name="Unknown", date="Unknown", total_amount=0.0, summary="Failed to parse document.")

def ask_llm_with_context(user_id: str, question: str) -> str:
    from app.database import query_relevant_chunks
    context = query_relevant_chunks(user_id=user_id, query=question)
    
    system_prompt = (
        "You are an AI assistant helping a user analyze their uploaded document.\n"
        "Use ONLY the following pieces of extracted context to answer the user's question.\n"
        "If you don't know the answer or if it's not in the context, say exactly that you cannot find it in the document.\n\n"
        f"--- CONTEXT START ---\n{context}\n--- CONTEXT END ---"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error creating chat response: {e}"