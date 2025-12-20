import { useState, useEffect } from 'react';
import { 
  queryRAGAgent, 
  queryRAGAgentWithPageContext, 
  startChatSession, 
  sendChatMessage, 
  getChatHistory 
} from '../services/api';

const useRAGAgent = () => {
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize a chat session when the hook is first used
  useEffect(() => {
    const initializeSession = async () => {
      try {
        const sessionData = await startChatSession();
        setSessionId(sessionData.session_id);
      } catch (err) {
        console.error('Failed to initialize chat session:', err);
        setError('Failed to initialize chat session');
      }
    };

    initializeSession();
  }, []);

  const query = async (question, pageContext = null) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await queryRAGAgent(question, pageContext);
      return response;
    } catch (err) {
      console.error('Error querying RAG agent:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const queryWithPageContext = async (question, pageUrl) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await queryRAGAgentWithPageContext(question, pageUrl);
      return response;
    } catch (err) {
      console.error('Error querying RAG agent with page context:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (question, pageContext = null) => {
    if (!sessionId) {
      throw new Error('No active session');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(sessionId, question, pageContext);
      return response;
    } catch (err) {
      console.error('Error sending chat message:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getHistory = async () => {
    if (!sessionId) {
      throw new Error('No active session');
    }

    try {
      const history = await getChatHistory(sessionId);
      return history;
    } catch (err) {
      console.error('Error getting chat history:', err);
      setError(err.message);
      throw err;
    }
  };

  return {
    sessionId,
    isLoading,
    error,
    query,
    queryWithPageContext,
    sendMessage,
    getHistory,
  };
};

export default useRAGAgent;