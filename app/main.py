"""
Document RAG System — production API.

Endpoints:
  POST /upload/{session_id}   — upload a PDF, builds its index for that session
  POST /ask/{session_id}      — ask a question about the uploaded document
  POST /summarize/{session_id} — get a summary of the uploaded document
  GET  /history/{session_id}  — view the conversation history for a session
  GET  /health                — health check for deployment monitoring
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.document_processor import extract_text_from_pdf, detect_document_type, chunk_text
from app.rag_engine import build_index, retrieve_and_rerank
from app.llm_client import build_prompt, generate_answer
from app.session_store import save_session, get_session, add_to_history

app = FastAPI(
    title="Document RAG System",
    description="Upload a PDF, ask questions, get grounded answers with citations.",
    version="2.0.0",
)


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload/{session_id}")
async def upload_pdf(session_id: str, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from this PDF.")

    chunks = chunk_text(text)
    index = build_index(chunks)
    doc_type = detect_document_type(text)

    save_session(session_id, chunks, index, doc_type)

    return {
        "message": "Document uploaded successfully.",
        "detected_type": doc_type,
        "chunk_count": len(chunks),
    }


@app.post("/ask/{session_id}")
def ask_question(session_id: str, payload: Question):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="No document found for this session. Upload one first.")

    results = retrieve_and_rerank(payload.question, session.chunks, session.index)
    context_chunks = [r["text"] for r in results]

    prompt = build_prompt(payload.question, context_chunks, session.doc_type, history=session.history)
    answer = generate_answer(prompt)

    add_to_history(session_id, payload.question, answer)

    return {
        "answer": answer,
        "sources": [{"chunk_id": r["chunk_id"], "relevance_score": round(r["relevance_score"], 3)} for r in results],
    }


@app.post("/summarize/{session_id}")
def summarize_document(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="No document found for this session. Upload one first.")

    context_chunks = session.chunks[:5]
    prompt = build_prompt("Provide a professional summary of this document.", context_chunks, session.doc_type)
    summary = generate_answer(prompt)

    return {"summary": summary}


@app.get("/history/{session_id}")
def get_history(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="No session found.")
    return {"history": session.history}
