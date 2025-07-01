from quart import Quart, request, jsonify
from quart_cors import cors
from rag import run_rag, tts
import time
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

app = Quart(__name__)
# Enable CORS for all routes
app = cors(app, allow_origin="*")

# Mimic OpenAI chat completion endpoint
@app.route('/v1/chat/completions', methods=['POST'])
async def chat_completions():
    try:
        # Receive JSON package
        data = await request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        model = data.get('model', os.getenv('RAG_MODEL'))
        messages = data.get('messages', [])
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400
        
        # Extract the user query from the messages
        user_query = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), None)
        if not user_query:
            return jsonify({'error': 'No user query found'}), 400
        
        # Provides instructional context
        # Note: Not sure if it is working as expected
        # system_promt = (
            # 'You are a helpful assistant that answers questions.'
        # )
        
        # Sends prompt to RAG system
        # prompt_input = f'{system_promt}\n\nUser: {user_query}'
        prompt_input = f'user: {user_query}'
        rag_response = run_rag(prompt_input)
        
        # Constructing the response in the OpenAI API format
        response = {
            'id': f'chatcmpl-{uuid.uuid4().hex[:10]}',
            'object': 'chat.completion',
            'created': int(time.time()),
            'model': model,
            'choices': [
            {
                'index': 0,
                'message':{
                    'role': 'assistant',
                    'content': rag_response['result']
                }
                ,
                'finish_reason': 'stop'
            }],
            # Placeholder as Ollama does not provide usage stats
            'usage': {
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0
            }
        }    
        
        rag_result = rag_response['result']
        tts(rag_result)  # Call TTS function to play the audio response
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    # Run with Hypercorn or alternative ASGI server in prod
    app.run(debug=True, port=5000)