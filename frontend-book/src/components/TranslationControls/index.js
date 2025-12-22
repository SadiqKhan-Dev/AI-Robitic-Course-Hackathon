import React, { useState, useEffect } from 'react';
import useTranslation from '../../hooks/useTranslation';
import './TranslationControls.css';

const TranslationControls = ({
  content,
  onTranslate,
  onLanguageChange,
  currentLanguage,
  defaultTargetLanguage = 'es',
  showComparison = false,
  onSelectionTranslate
}) => {
  const { supportedLanguages, isLoading, translateText, getLanguageName, translateSelection } = useTranslation();
  const [targetLanguage, setTargetLanguage] = useState(defaultTargetLanguage);
  const [comparisonLanguages, setComparisonLanguages] = useState([]);
  const [showComparisonPanel, setShowComparisonPanel] = useState(false);

  useEffect(() => {
    if (currentLanguage) {
      setTargetLanguage(currentLanguage);
    }
  }, [currentLanguage]);

  const handleTranslate = async () => {
    if (!content) return;

    try {
      const result = await translateText(content, 'en', targetLanguage);
      onTranslate(result.translated_content, targetLanguage);
    } catch (error) {
      console.error('Translation failed:', error);
    }
  };

  const handleSelectionTranslate = async (fullContent, selectionStart, selectionEnd, sourceLang, targetLang) => {
    if (!onSelectionTranslate) return;

    try {
      const result = await translateSelection(fullContent, selectionStart, selectionEnd, sourceLang, targetLang);
      onSelectionTranslate(result.translated_content, targetLang);
    } catch (error) {
      console.error('Selection translation failed:', error);
    }
  };

  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setTargetLanguage(newLanguage);
    onLanguageChange(newLanguage);
  };

  const toggleComparisonPanel = () => {
    setShowComparisonPanel(!showComparisonPanel);
  };

  const addComparisonLanguage = (langCode) => {
    if (!comparisonLanguages.includes(langCode) && langCode !== targetLanguage) {
      setComparisonLanguages([...comparisonLanguages, langCode]);
    }
  };

  const removeComparisonLanguage = (langCode) => {
    setComparisonLanguages(comparisonLanguages.filter(code => code !== langCode));
  };

  return (
    <div className="translation-controls">
      <div className="translation-selector">
        <label htmlFor="language-select">Translate to:</label>
        <select
          id="language-select"
          value={targetLanguage}
          onChange={handleLanguageChange}
          disabled={isLoading}
          className={isLoading ? 'loading' : ''}
        >
          {supportedLanguages
            .filter(lang => lang.is_enabled)
            .map(lang => (
              <option key={lang.language_code} value={lang.language_code}>
                {lang.language_name} ({lang.language_code})
              </option>
            ))}
        </select>
      </div>

      <button
        onClick={handleTranslate}
        disabled={isLoading || !content}
        className={`translate-btn ${isLoading ? 'loading' : ''}`}
      >
        {isLoading ? 'Translating...' : 'Translate'}
      </button>

      {showComparison && (
        <button
          onClick={toggleComparisonPanel}
          className="compare-btn"
        >
          {showComparisonPanel ? 'Hide Comparison' : 'Compare Languages'}
        </button>
      )}

      {showComparisonPanel && (
        <div className="comparison-panel">
          <h4>Compare with other languages:</h4>
          <div className="comparison-languages">
            {supportedLanguages
              .filter(lang => lang.is_enabled && lang.language_code !== targetLanguage)
              .map(lang => (
                <div key={lang.language_code} className="comparison-option">
                  <input
                    type="checkbox"
                    id={`compare-${lang.language_code}`}
                    checked={comparisonLanguages.includes(lang.language_code)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        addComparisonLanguage(lang.language_code);
                      } else {
                        removeComparisonLanguage(lang.language_code);
                      }
                    }}
                  />
                  <label htmlFor={`compare-${lang.language_code}`}>
                    {lang.language_name} ({lang.language_code})
                  </label>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TranslationControls;