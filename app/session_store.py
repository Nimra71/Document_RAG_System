"""
Simple in-memory store keyed by session_id.

Note: this resets if the server restarts or if you scale to multiple instances
(Cloud Run can spin up more than one). For a portfolio/demo project this is fine.
If you later want persistence across restarts/instances, swap this for Redis —
worth mentioning in an interview as a known next step.
"""
from dataclasses import dataclass, field


@dataclass
class DocumentSession:
    chunks: list[str]
    index: object
    doc_type: str
    history: list[dict] = field(default_factory=list)


_sessions: dict[str, DocumentSession] = {}


def save_session(session_id: str, chunks: list[str], index, doc_type: str):
    _sessions[session_id] = DocumentSession(chunks=chunks, index=index, doc_type=doc_type)


def get_session(session_id: str) -> DocumentSession | None:
    return _sessions.get(session_id)


def add_to_history(session_id: str, question: str, answer: str):
    session = _sessions.get(session_id)
    if session:
        session.history.append({"question": question, "answer": answer})
