import React, { useState } from 'react';

const QueryInput = ({ onSubmit, disabled = false }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSubmit(query.trim());
      setQuery(''); // Clear the input after submitting
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (query.trim() && !disabled) {
        handleSubmit(e);
      }
    }
  };

  return (
    <form className="query-input-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <textarea
          className="query-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the book content..."
          disabled={disabled}
          rows="1"
          aria-label="Enter your question"
        />
        <button 
          type="submit" 
          className="submit-button"
          disabled={disabled || !query.trim()}
          aria-label="Submit question"
        >
          <span>→</span>
        </button>
      </div>
    </form>
  );
};

export default QueryInput;