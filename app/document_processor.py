"""
Handles PDF text extraction, chunking, and document type detection.
"""
from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes (not a file path — works with uploads)."""
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def detect_document_type(text: str) -> str:
    text_lower = text.lower()
    if "cgpa" in text_lower or "experience" in text_lower or "skills" in text_lower:
        return "Resume / CV"
    elif "abstract" in text_lower or "methodology" in text_lower:
        return "Research Paper"
    elif "coursework" in text_lower or "university" in text_lower:
        return "Academic Document"
    return "General Document"


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """Simple sliding-window chunking, same core approach as the original project."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks
