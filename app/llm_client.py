"""
Handles calls to Groq's API for answer generation.

This replaces the original project's local unsloth/llama-3-8b-bnb-4bit model,
which required a GPU. Groq's free tier lets us run entirely on CPU-only,
free-tier cloud hosting, since generation happens over the network instead
of on the host machine.
"""
import os
from groq import Groq

_MODEL = "llama-3.1-8b-instant"  # fast + free-tier friendly
_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set.")
        _client = Groq(api_key=api_key)
    return _client


def build_prompt(question: str, context_chunks: list[str], doc_type: str, history: list[dict] | None = None) -> str:
    context = "\n\n".join(context_chunks)
    history_block = ""
    if history:
        history_lines = [f"Q: {h['question']}\nA: {h['answer']}" for h in history[-3:]]
        history_block = "Previous conversation (for context on follow-up questions):\n" + "\n\n".join(history_lines) + "\n\n"

    return f"""You are a professional document analyst.

The document type is: {doc_type}

{history_block}Using ONLY the document content below, answer the question clearly and specifically.
Avoid short or generic statements. If the answer isn't in the content, say so — do not make things up.

Document Content:
{context}

Question:
{question}

Answer:"""


def generate_answer(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.25,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
