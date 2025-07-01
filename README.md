# Kelley-HOPE-25---E-Learning-Project

# How to run
Add .env file with RAG_MODEL = 'your model name here'

Install dependencies from requirements_rag.txt

Run \_\_init\_\_.py

Read Frontend README to run web interface

# Currently Implemented
- RAG Model
- Integrated Chatbot
- TTS

# ToDo for MVP:
- Fix latency issues - takes a long time to generate response and then generate tts reply (high priority)
- Fix delay between displaying response and tts
    - Currently, TTS talks first, and then the response is sent to the chatbox after
- Look into other TTS models

# Other things (not sure if required):
- Real-time streamed responses
- Implement STT for user input
- Add node.js middleware for authentication and rate limiting
- Adding guardrails in system prompt for LLM (possible solution is custom llm)
- Animated digital avatar
- Lip sync
