# Kelley-HOPE-25---E-Learning-Project

## Overview

This project is a Retrieval-Augmented Generation (RAG) system with a React-based frontend and a Python backend.

* **Frontend**: Provides chat interface and HeyGen streaming avatar.
* **Backend**: Handles PDF ingestion, embedding, vector storage, LLM-based retrieval

## Folder Structure
```
/Frontend
    ├── src/
    ├── public/
    ├── .env
    ├── package.json
    └── ... (React app files)

/RAG
    ├── __init__.py
    ├── rag.py
    ├── embedding.py
    ├── pdfprocess.py
    ├── config.yaml
    └── ... (Python backend files)
```
## Setup Instructures

**Backend (Python in RAG)**

1. **Install dependencies**
    * Dependencies are managed using [Poetry] (https://python-poetry.org/docs/#installation)
    * In directory where pyproject.toml is located, run:
    `poetry install`
    * To activate virtual environment, run:
    `poetry shell`

2. **Configure environment**
    * Place a .env file in the project root
    * Set any required environmental variables (API Keys)

3. **Configure YAML**
    * Edit config.yaml to set model names, chunk sizes, and other parameters

4. **Run the backend**
    * Start with
    `poetry run python __init__.py`

**Frontend (React in /Frontend)**

1. **Install dependencies**
```
cd Frontend
npm install
```

2. **Configure environment**
    * Place a .env file in /Frontend (same level as package.json)
    * Add HeyGen API key:

3. **Run the frontend**
`npm start`
    * App runs on http://localhost:3000

## Key Components

**Backend**

* rag.py: Main orchestration for RAG, embedding, retrieval, and TTS.
* embedding.py: Handles document embedding and storage in ChromaDB.
* pdfprocess.py: Loads and splits PDFs into chunks for embedding.
* config.yaml: Central configuration for models, chunking, TTS, etc.
* __init__.py: Quart API exposing /v1/chat/completions for chat.

**Frontend**

* src/SimpleChatUI.jsx: Main chat interface, handles user input, displays messages, integrates HeyGen avatar and speech-to-text.
* .env: Stores frontend secrets (HeyGen API key).
* package.json: Lists dependencies, scripts.

##
**Development Notes**

* **PDF Embedding:**
    Run embed_pdf('filename.pdf') in rag.py to process and store new documents.
* **LLM Switching:**
    The backend is set up to use Ollama by default, but can be switched to Gemini by editing the config and code.
* **TTS:** (Deprecated if using HeyGen)
    Uses Coqui TTS for local speech synthesis.
* **HeyGen Avatar:**
    The frontend uses the HeyGen Streaming Avatar SDK. The API key must be set in /Frontend/.env.