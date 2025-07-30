import React, { useRef, useState, useEffect } from 'react';
import StreamingAvatar, {
  AvatarQuality,
  StreamingEvents,
  ElevenLabsModel,
  VoiceEmotion,
  TaskType,
} from '@heygen/streaming-avatar';

export default function ConnectedChatInterface() {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [apiUrl] = useState('http://localhost:5000/v1/chat/completions'); // Updated for RAG backend

  function handleChange(e) {
    setInputValue(e.target.value);
  }

  async function sendMessage(message) {
    try {
      // Updated to use a more generic RAG endpoint
      const response = await fetch(`${apiUrl}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'qwen3:8b',
          messages: [
            {role: 'user', content: message}
          ],  // Changed from 'messages' to 'query'
          // Add any other parameters your RAG backend expects
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Adjust this based on your backend's response structure
      return data.choices?.[0]?.message?.content.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async function handleSubmit(e, overrideText = null) {
    if (e?.preventDefault) e.preventDefault();
    const userMessage = overrideText ?? inputValue.trim();
    if (!userMessage || isLoading) return;
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send message to backend and get response
      const assistantResponse = await sendMessage(userMessage);
      
      // Add assistant response to chat
      setMessages(prev => [...prev, { role: 'assistant', content: assistantResponse }]);

      // Using HeyGen Avatar
      await avatarRef.current?.speak({
        text: assistantResponse,
        task_type: TaskType.REPEAT,
        taskMode: 'SYNC'
      })

    } catch (error) {
      // Add error message to chat
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: `Error: ${error.message}. Make sure your RAG backend is running on ${apiUrl}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  }

  function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech Recognition API is not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsRecording(false);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      handleSubmit(null, transcript);
    };

    recognition.start();
  }

  const avatarRef = useRef(null);

  useEffect(() => {
    const avatar = new StreamingAvatar({ token: '' }); // Retrieve HeyGen API Key | TODO: Use env variable
    avatarRef.current = avatar;

    avatar.on(StreamingEvents.STREAM_READY, (event) => {
      const stream = event.detail;
      const videoElement = document.getElementById('heygen-avatar');
      if (videoElement) {
        videoElement.srcObject = stream;
      }
    });

    avatar.createStartAvatar({
      avatarName: 'Elenora_IT_Sitting_public',
      quality: AvatarQuality.Low,
      voice: {
        rate: 1.0,
        emotion: VoiceEmotion.EXCITED,
        model: ElevenLabsModel.eleven_flash_v2_5,
      },
      language: 'en'
    });

    // Optional: cleanup on unmount
    return () => {
      avatar?.stop?.();
    };
  }, []);

  return (
    <div style={{ height: '100vh', width: '100vw', position: 'relative', backgroundColor: '#f9fafb' }}>
      {/* Header */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '16px 32px', 
        borderBottom: '1px solid #e5e7eb',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#374151', margin: 0 }}>
          RAG Chat Interface
        </h1>
        <p style={{ color: '#6b7280', margin: '4px 0 0 0', fontSize: '14px' }}>
          Connected to: {apiUrl} 
          <span style={{ 
            display: 'inline-block', 
            width: '8px', 
            height: '8px', 
            backgroundColor: '#10b981', 
            borderRadius: '50%', 
            marginLeft: '8px' 
          }}></span>
        </p>
      </div>

      {/* Heygen Avatar */}
      <div style={{ display: 'flex', justifyContent: 'center', margin: '24px 0' }}>
        <video
          id="heygen-avatar"
          autoPlay
          muted
          style={{ width: 240, height: 320, borderRadius: 16, background: '#000' }}
        />
      </div>

      {/* Messages area */}
      <div style={{ 
        height: 'calc(100vh - 200px)', 
        overflowY: 'auto', 
        padding: '20px 32px',
        paddingBottom: '120px' // Space for input
      }}>
        {messages.length === 0 && (
          <div style={{ 
            textAlign: 'center', 
            color: '#6b7280', 
            marginTop: '50px',
            fontSize: '16px'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
            <p>Start a conversation with your RAG system!</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>
              Ask questions about your documents and get AI-powered answers.
            </p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div 
            key={index}
            style={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px'
            }}
          >
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '18px',
              backgroundColor: message.role === 'user' 
                ? '#3b82f6' 
                : message.role === 'error' 
                ? '#ef4444' 
                : 'white',
              color: message.role === 'user' || message.role === 'error' ? 'white' : '#374151',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              border: message.role === 'assistant' ? '1px solid #e5e7eb' : 'none',
              wordWrap: 'break-word',
              whiteSpace: 'pre-wrap'
            }}>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '4px' }}>
                {message.role === 'user' ? 'You' : message.role === 'error' ? 'Error' : 'Assistant'}
              </div>
              {message.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '18px',
              backgroundColor: 'white',
              color: '#6b7280',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid #e5e7eb',
                borderTop: '2px solid #3b82f6',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              Assistant is thinking...
            </div>
          </div>
        )}
      </div>
      
      {/* Fixed input at bottom */}
      <div style={{
        position: 'fixed',
        bottom: '0',
        left: '0',
        right: '0',
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb',
        padding: '20px 32px',
        boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ display: 'flex', gap: '12px', maxWidth: '800px', margin: '0 auto' }}>
          <input
            type="text"
            value={inputValue}
            onChange={handleChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSubmit(e);
              }
            }}
            placeholder="Ask a question about your documents..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '24px',
              outline: 'none',
              fontSize: '14px',
              backgroundColor: isLoading ? '#f9fafb' : 'white',
              opacity: isLoading ? 0.7 : 1
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={!inputValue.trim() || isLoading}
            style={{
              padding: '12px 24px',
              backgroundColor: isLoading || !inputValue.trim() ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '24px',
              cursor: isLoading || !inputValue.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              minWidth: '80px'
            }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>
      
      {/* Voice input button */}
      <div style = {{
        position: 'fixed',
        bottom: '0',
        left: '0',
        right: '0',
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb',
        padding: '20px 32px',
        boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ display: 'flex', gap: '12px', maxWidth: '800px', margin: '0 auto' }}>
          <button
            onClick={startListening}
            disabled={isLoading}
            style={{
              padding: '0 16px',
              border: 'none',
              backgroundColor: isRecording ? '#10b981' : '#f3f4f6',
              color: isRecording ? 'white' : '#374151',
              borderRadius: '50%',
              fontSize: '20px',
              cursor: 'pointer',
              width: '44px',
              height: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Click to speak"
          >Test
          </button>
          <input
            type="text"
            value={inputValue}
            onChange={handleChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSubmit(e);
            }}
            placeholder="Ask a question about your documents..."
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '24px',
              outline: 'none',
              fontSize: '14px',
              backgroundColor: isLoading ? '#f9fafb' : 'white',
              opacity: isLoading ? 0.7 : 1
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={!inputValue.trim() || isLoading}
            style={{
              padding: '12px 24px',
              backgroundColor: isLoading || !inputValue.trim() ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '24px',
              cursor: isLoading || !inputValue.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              minWidth: '80px'
            }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>
      {/* CSS for spinning animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}