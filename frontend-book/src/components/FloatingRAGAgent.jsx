import React, { useState, useEffect } from 'react';
import './FloatingRAGAgent.css';
import ChatWindow from './ChatWindow';

const FloatingRAGAgent = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // Initialize the agent when component mounts
  useEffect(() => {
    // In a real implementation, you might initialize a session here
    setIsInitialized(true);
  }, []);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const closeChat = () => {
    setIsOpen(false);
  };

  if (!isInitialized) {
    return null; // Or a loading indicator
  }

  return (
    <div className="floating-rag-agent">
      {isOpen ? (
        <ChatWindow 
          sessionId={sessionId} 
          onClose={closeChat} 
          pageContext={typeof window !== 'undefined' ? window.location.href : ''}
        />
      ) : (
        <button 
          className="floating-agent-button"
          onClick={toggleChat}
          aria-label="Open RAG Agent Chat"
        >
          <div className="chat-icon">🤖</div>
        </button>
      )}
    </div>
  );
};

export default FloatingRAGAgent;