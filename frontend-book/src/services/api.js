// API service for interacting with the backend RAG agent

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Query the RAG agent with a question
 * @param {string} question - The question to ask
 * @param {string} pageContext - Optional URL of the current page for context
 * @returns {Promise<Object>} The response from the RAG agent
 */
export const queryRAGAgent = async (question, pageContext = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        page_context: pageContext
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error querying RAG agent:', error);
    throw error;
  }
};

/**
 * Query the RAG agent with page context
 * @param {string} question - The question to ask
 * @param {string} pageUrl - URL of the page to focus on
 * @returns {Promise<Object>} The response from the RAG agent
 */
export const queryRAGAgentWithPageContext = async (question, pageUrl) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query/page`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        page_url: pageUrl
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error querying RAG agent with page context:', error);
    throw error;
  }
};

/**
 * Start a new chat session
 * @returns {Promise<Object>} The session information
 */
export const startChatSession = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error starting chat session:', error);
    throw error;
  }
};

/**
 * Send a message in a chat session
 * @param {string} sessionId - The session ID
 * @param {string} question - The question to ask
 * @param {string} pageContext - Optional URL of the current page for context
 * @returns {Promise<Object>} The response from the RAG agent
 */
export const sendChatMessage = async (sessionId, question, pageContext = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        page_context: pageContext
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

/**
 * Get chat history for a session
 * @param {string} sessionId - The session ID
 * @returns {Promise<Object>} The chat history
 */
export const getChatHistory = async (sessionId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${sessionId}/history`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting chat history:', error);
    throw error;
  }
};

/**
 * Check API health
 * @returns {Promise<Object>} Health check response
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/../health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};