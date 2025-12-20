import React, { useState, useEffect, useRef } from 'react';
import QueryInput from './QueryInput';
import { queryRAGAgent } from '../services/api';

const ChatWindow = ({ sessionId, onClose, pageContext }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleQuerySubmit = async (question) => {
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: question,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the backend API to get response
      const response = await queryRAGAgent(question, pageContext);
      
      // Add agent response to chat
      const agentMessage = {
        id: Date.now() + 1,
        text: response.answer,
        sender: 'agent',
        sources: response.sources,
        confidence: response.confidence,
        fallbackUsed: response.fallback_used,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error getting response from RAG agent:', error);
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I encountered an error processing your request. Please try again.",
        sender: 'agent',
        isError: true,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-title">Book RAG Agent</div>
        <button className="close-button" onClick={onClose} aria-label="Close chat">
          ×
        </button>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Hello! I'm your book assistant. Ask me anything about this book, and I'll find the answer in the content.</p>
            <p>If I don't know the answer, I'll tell you directly.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.sender}-message`}
            >
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                {message.sources && message.sources.length > 0 && !message.fallbackUsed && (
                  <div className="message-sources">
                    <small>Sources: {message.sources.length} content chunks referenced</small>
                  </div>
                )}
                {message.isError && (
                  <div className="error-indicator">⚠️</div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message agent-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-area">
        <QueryInput onSubmit={handleQuerySubmit} disabled={isLoading} />
      </div>
    </div>
  );
};

export default ChatWindow;