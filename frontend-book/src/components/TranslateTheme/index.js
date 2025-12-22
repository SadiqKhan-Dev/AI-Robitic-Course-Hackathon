import React, { useState, useEffect } from 'react';
import { useLocation } from '@docusaurus/router';
import { translate } from '@docusaurus/Translate';
import TranslationToggle from '../components/TranslationToggle';
import TranslationControls from '../components/TranslationControls';
import TranslatedContent from '../components/TranslatedContent';

const TranslateTheme = ({ children }) => {
  const location = useLocation();
  const [originalContent, setOriginalContent] = useState('');
  const [translatedContent, setTranslatedContent] = useState('');
  const [currentLang, setCurrentLang] = useState('en');
  const [showTranslation, setShowTranslation] = useState(false);
  
  // Extract content from children if it's a string
  useEffect(() => {
    if (typeof children === 'string') {
      setOriginalContent(children);
    } else {
      // If children is a React element, we might need to extract text differently
      setOriginalContent(children?.props?.children || '');
    }
  }, [children]);

  const handleTranslate = (translated, lang) => {
    setTranslatedContent(translated);
    setCurrentLang(lang);
    setShowTranslation(true);
  };

  const handleLanguageChange = (lang) => {
    setCurrentLang(lang);
  };

  const toggleTranslation = () => {
    setShowTranslation(!showTranslation);
  };

  return (
    <div className="translate-theme-container">
      <TranslationControls
        content={originalContent}
        onTranslate={handleTranslate}
        onLanguageChange={handleLanguageChange}
        currentLanguage={currentLang}
      />
      
      <TranslatedContent
        originalContent={originalContent}
        translatedContent={translatedContent}
        targetLanguage={currentLang}
        showOriginal={!showTranslation}
      />
      
      <TranslationToggle 
        onToggle={toggleTranslation} 
        isTranslated={showTranslation} 
      />
    </div>
  );
};

export default TranslateTheme;