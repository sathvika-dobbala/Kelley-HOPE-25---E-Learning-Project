# Kelley-HOPE-25---E-Learning-Project

# Updates (7/8/2025)
- Fixed latency issue by switching to CoquiTTS

# Requirements
- Python 3.10
- Ollama service running locally

# How to run
1. Clone the repository
```
git clone https://github.com/sathvika-dobbala/Kelley-HOPE-25---E-Learning-Project
```
2. Setup environmental variables
Create .env file in root and specify RAG model
```
RAG_MODEL = 'model_name'
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Run RAG backend
```
python __init__.py
```
5. Start frontend service

# Currently Implemented
- RAG Model
- Integrated Chatbot
- TTS

# Todo
- Implement LLM streaming mode (main priority)
- STT (low priority)
- Lip Sync with Avatar (if possible)

# Other things (not sure if required):
- Add node.js middleware for authentication and rate limiting
- Adding guardrails in system prompt for LLM (possible solution is custom llm)
