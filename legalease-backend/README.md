# LegalEase BD - Backend

This directory contains the backend infrastructure for **LegalEase BD**, a cloud-based AI legal assistant. Built with Python, it serves as the core intelligence engine, handling data processing, vector embeddings, and API communication for the frontend.

## 🌟 Key Features

* **High-Performance API:** Utilizes **FastAPI** to provide robust, asynchronous REST API endpoints for seamless frontend integration.
* **Retrieval-Augmented Generation (RAG):** Implements a custom RAG pipeline to dynamically retrieve highly relevant legal context before generating responses, ensuring accuracy and grounding the AI in factual data.
* **Vector Search:** Integrates **Pinecone** as the vector database for highly efficient semantic search and embedding storage.
* **Cloud-Ready:** Structured for scalable cloud deployment and efficient resource management.

## 🛠️ Technology Stack

* **Language:** Python 3.8+
* **Framework:** FastAPI
* **Vector Database:** Pinecone
* **Architecture:** Retrieval-Augmented Generation (RAG)

## 🚀 Local Development Setup

### 1. Prerequisites
Ensure you have Python installed on your machine. You will also need active API keys for:
* Pinecone (for vector storage and retrieval)
* Your chosen LLM Provider (e.g., Google Gemini, OpenAI)

### 2. Installation
Navigate to the backend directory and set up a Python virtual environment:

```bash
# From the root of the repository
cd legalease-backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS (Arch Linux/Zorin OS):
source venv/bin/activate
# On Windows:
venv\Scripts\activate
