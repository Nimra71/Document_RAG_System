!pip install -q unsloth transformers accelerate bitsandbytes
!pip install -q sentence-transformers faiss-cpu pypdf

from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=4096,
    load_in_4bit=True,
)

FastLanguageModel.for_inference(model)

from pypdf import PdfReader
import faiss
import numpy as np

def detect_document_type(text):
    text_lower = text.lower()

    if "cgpa" in text_lower or "experience" in text_lower or "skills" in text_lower:
        return "Resume / CV"
    elif "abstract" in text_lower or "methodology" in text_lower:
        return "Research Paper"
    elif "coursework" in text_lower or "university" in text_lower:
        return "Academic Document"
    else:
        return "General Document"


from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def process_pdf(file):
    reader = PdfReader(file.name)
    text = ""

    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()

    # chunking
    def chunk_text(text, chunk_size=400, overlap=50):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    chunks = chunk_text(text)

    embeddings = embedder.encode(chunks, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    doc_type = detect_document_type(text)

    return chunks, index, doc_type

def retrieve_chunks(question, chunks, index, k=4):
    query_embedding = embedder.encode([question])
    _, indices = index.search(np.array(query_embedding), k)
    return [chunks[i] for i in indices[0]]

def build_prompt(question, context_chunks):
    context = "\n".join(context_chunks)
    return f"""
You are a professional document analyst.

The document type is: {stored_doc_type}

Using ONLY the document content below:
- Clearly explain what this document is
- Describe its purpose
- Mention what kind of information it contains

Avoid short or generic statements.

Document Content:
{context}

Question:
{question}

Answer:
"""

import torch
def generate_answer(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    output = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.25,
        top_p=0.9,
    )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return text.split("Answer:")[-1].strip()

def ask_pdf(question):
    context = retrieve_chunks(question)
    prompt = build_prompt(question, context)
    return generate_answer(prompt)

def summarize_document():
    if stored_chunks is None:
        return "Please upload a document first."

    context = stored_chunks[:5]
    prompt = build_prompt("Provide a professional summary of this document.", context)
    return generate_answer(prompt)

!pip install -q gradio

import gradio as gr

stored_chunks = None
stored_index = None
stored_doc_type = None

def upload_pdf(file):
    global stored_chunks, stored_index, stored_doc_type

    if file is None:
        return "Please upload a PDF file."

    stored_chunks, stored_index, stored_doc_type = process_pdf(file)
    return f"Document uploaded successfully. Detected type: {stored_doc_type}"

def ask_question(question):
    if stored_chunks is None or stored_index is None:
        return "Please upload a document first."

    context = retrieve_chunks(question, stored_chunks, stored_index)
    prompt = build_prompt(question, context)
    return generate_answer(prompt)


import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("# 📄 Document Understanding System")

    file = gr.File(label="Upload PDF")
    upload_status = gr.Textbox(label="Status", interactive=False)

    upload_btn = gr.Button("Upload Document")
    upload_btn.click(upload_pdf, inputs=file, outputs=upload_status)

    question = gr.Textbox(
        label="Ask a question",
        placeholder="e.g. What is this document about?",
        lines=2
    )

    answer = gr.Textbox(label="Answer", lines=8)

    ask_btn = gr.Button("Ask Question")
    summarize_btn = gr.Button("Summarize Document")

    ask_btn.click(ask_question, inputs=question, outputs=answer)
    summarize_btn.click(summarize_document, outputs=answer)

demo.launch()
