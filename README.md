# Document_RAG_System
# 📄 Intelligent Document Analysis System using RAG & Quantized LLMs

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technical Architecture](#technical-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Output Examples](#output-examples)
- [License](#license)

---

## Project Overview
This project is an **intelligent document analysis system** that allows users to upload PDF documents and ask natural language questions about their content. It leverages **Retrieval-Augmented Generation (RAG)** and a **dynamic 4-bit quantized Unsloth language model** for memory-efficient inference, providing **grounded, professional responses** and summaries.

---

## Key Features
- Upload any PDF and automatically detect its document type (Resume, Academic, Research Paper, General)  
- Ask natural language questions and get **professional, grounded answers**  
- Summarize uploaded documents **with one click**  
- Semantic retrieval using **FAISS embeddings**  
- Low memory inference with **dynamic 4-bit quantized LLMs**  
- Interactive, clean UI using **Gradio**  

---

## Technical Architecture
```mermaid```
graph TD

A[Upload PDF] --> B[Document Type Detection]

B --> C[Chunking + Embeddings]

C --> D[FAISS Retrieval]

D --> E[Quantized LLM Answer Generation]

E --> F[User Interface Output]

## Installation

Clone the repository:

git clone https://github.com/yourusername/Document_RAG_System.git
cd Document_RAG_System


Install dependencies:

pip install -r requirements.txt


Run the interface:

python scripts/document_rag_system.py
Or open notebooks/Document_RAG_Notebook.ipynb in Colab

## Usage

Open the interface (local or Colab)

Upload a PDF document

Check the detected document type

Ask questions in natural language

Click Summarize Document to get a professional summary

## Output Examples

| Question | Example Output |
|----------|----------------|
| What is this document about? | Provides a concise summary of the document’s main content. For example, if it’s an academic paper, it summarizes the abstract and key findings; if it’s a report or notes, it summarizes the main topics. |
| Summarize document | Generates a high-level summary highlighting the key sections, ideas, or information contained in the document, regardless of type. |
| Ask a specific question about content | Answers accurately based on the document’s content. For example, “What are the main results?” or “Who is mentioned?” returns grounded answers from the PDF. |


## License

MIT License
