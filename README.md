# LegalEase BD: Cloud-Based AI Legal Assistant

Welcome to the repository for **LegalEase BD**, an intelligent, cloud-based AI legal assistant. This project leverages natural language processing and modern full-stack web development to deliver context-aware legal information and insights.

## 🚀 Live Demo

Experience the live application here: **[LegalEase BD Web App](https://nlp-project-ashy.vercel.app)**

## 📂 Repository Structure

This repository is organized into a full-stack architecture with dedicated frontend and backend directories:

- **`legalease-backend/`**: The core intelligence engine, data processing, and API layer.
- **`legalease-frontend/`**: The user-facing interactive web application.

## 🛠️ Technical Stack & Architecture

### Backend (Python)
The backend is engineered for high-performance NLP operations and optimized data retrieval:
- **FastAPI:** Serves robust, high-speed API endpoints.
- **Retrieval-Augmented Generation (RAG):** Employs a custom RAG pipeline to dynamically retrieve relevant legal contexts, ensuring the AI's responses are accurate and grounded in factual data.
- **Pinecone:** Utilizes Pinecone as the vector database for highly efficient semantic search and embedding storage.

### Frontend (JavaScript / CSS / HTML)
The frontend delivers a seamless user experience, communicating smoothly with the backend REST APIs to provide real-time, conversational access to the legal assistant.

## ⚙️ Local Development & Setup

### Prerequisites
- **Python 3.8+** (for the backend environment)
- **Node.js & npm/yarn** (for the frontend environment)
- Necessary API Keys: Pinecone API Key, LLM Provider API Key (e.g., OpenAI, Google Gemini).

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd legalease-backend
