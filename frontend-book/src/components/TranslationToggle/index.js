import React, { useState } from 'react';
import './TranslationToggle.css';

const TranslationToggle = ({ onToggle, isTranslated, isLoading = false }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="translation-toggle-container">
      <div
        className={`translation-toggle ${isTranslated ? 'translated' : 'original'}`}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <button
          className={`toggle-btn ${isTranslated ? 'active' : ''} ${isLoading ? 'loading' : ''}`}
          onClick={onToggle}
          disabled={isLoading}
          aria-label={isTranslated ? "Show original content" : "Translate content"}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span> Translating...
            </>
          ) : (
            <>
              {isTranslated ? "🌐 Original" : "🌐 Translate"}
            </>
          )}
        </button>
        {showTooltip && !isLoading && (
          <div className="tooltip">
            {isTranslated ? "Show original content" : "Translate to your preferred language"}
          </div>
        )}
      </div>
    </div>
  );
};

export default TranslationToggle;