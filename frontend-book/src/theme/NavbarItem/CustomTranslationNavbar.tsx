import React, { useState, useEffect } from 'react';
import { useTranslation } from '@site/src/hooks/useTranslation';
import { mockTranslate } from '@site/src/services/mockTranslationService';
import './TranslationNavbar.css';

const CustomTranslationNavbar = (props) => {
  const { supportedLanguages, userPreferences, updatePreferences, translateText } = useTranslation();
  const [selectedLanguage, setSelectedLanguage] = useState(userPreferences?.defaultTargetLanguage || 'es');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    if (userPreferences?.defaultTargetLanguage) {
      setSelectedLanguage(userPreferences.defaultTargetLanguage);
    }
  }, [userPreferences]);

  const handleLanguageChange = (langCode) => {
    setSelectedLanguage(langCode);
    updatePreferences?.({ defaultTargetLanguage: langCode });
    setIsDropdownOpen(false);
  };

  const handleTranslateClick = async () => {
    if (isTranslating) return; // Prevent multiple simultaneous translations

    setIsTranslating(true);

    try {
      // Target the main content area of Docusaurus docs
      const mainContent = document.querySelector('#main-content') ||
                         document.querySelector('main') ||
                         document.querySelector('article') ||
                         document.querySelector('.container');

      if (!mainContent) {
        console.warn('No main content area found to translate');
        setIsTranslating(false);
        return;
      }

      // Extract the innerHTML to preserve structure, or fallback to text content
      const content = mainContent.innerHTML || mainContent.textContent || mainContent.innerText;

      if (content.trim() === '') {
        console.warn('No content to translate');
        setIsTranslating(false);
        return;
      }

      // For now, let's focus on translating to Urdu specifically if selected
      if (selectedLanguage === 'ur') {
        console.log('Translating to Urdu functionality activated');
      }

      // Show loading message to user
      console.log('Sending content to translation service...');

      try {
        // Attempt to translate using the actual service
        const result = await translateText(
          content,
          'en', // Assuming source language is English
          selectedLanguage,
          {
            preserveFormatting: true,
            preserveCodeBlocks: true,
            preserveTechnicalTerms: true
          }
        );

        console.log('Translation received from service:', result);

        // Temporarily store the original content for potential revert
        if (!mainContent.dataset.originalContent) {
          mainContent.dataset.originalContent = mainContent.innerHTML;
        }

        // Update the main content with the translated version
        mainContent.innerHTML = result.translated_content;

        console.log('Translation completed successfully');
      } catch (translationError) {
        console.warn('Translation service error:', translationError);

        // Fallback to mock translation if the backend service is not available
        console.log('Falling back to mock translation');

        // Create a temporary div to work with the content
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = content;

        // Get all text nodes and translate them
        const translateTextNodes = (node) => {
          if (node.nodeType === Node.TEXT_NODE) {
            if (node.textContent.trim() !== '') {
              // Translate the text content
              const translatedText = mockTranslate(node.textContent, 'en', selectedLanguage);
              node.textContent = translatedText;
            }
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Recursively process child nodes
            for (const child of node.childNodes) {
              translateTextNodes(child);
            }
          }
        };

        // Process the content
        for (const child of tempDiv.childNodes) {
          translateTextNodes(child);
        }

        // Update the main content with the mock-translated version
        mainContent.innerHTML = tempDiv.innerHTML;

        console.log('Mock translation completed');
      }
    } catch (error) {
      console.error('General error in translation:', error);
      alert(`Translation failed: ${error.message}`);
    } finally {
      setIsTranslating(false);
    }
  };

  const languageOptions = supportedLanguages.filter(lang => lang.is_enabled);

  return (
    <div className="translation-navbar-container">
      <div className="translation-dropdown">
        <button
          className="translation-navbar-button"
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          aria-expanded={isDropdownOpen}
          aria-haspopup="true"
          disabled={isTranslating}
        >
          <span className="translation-icon">🌐</span>
          <span className="translation-text">Translate</span>
          <span className="translation-arrow">{isDropdownOpen ? '▲' : '▼'}</span>
        </button>

        {isDropdownOpen && (
          <ul className="translation-dropdown-menu">
            {languageOptions.map((lang) => (
              <li key={lang.language_code}>
                <button
                  className={`translation-dropdown-item ${
                    selectedLanguage === lang.language_code ? 'translation-dropdown-item--active' : ''
                  }`}
                  onClick={() => handleLanguageChange(lang.language_code)}
                  disabled={isTranslating}
                >
                  {lang.language_name} ({lang.language_code.toUpperCase()})
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <button
        className="translation-action-button"
        onClick={handleTranslateClick}
        title={`Translate to ${supportedLanguages.find(lang => lang.language_code === selectedLanguage)?.language_name || selectedLanguage}`}
        disabled={isTranslating}
      >
        <span>{isTranslating ? 'Translating...' : `To ${supportedLanguages.find(lang => lang.language_code === selectedLanguage)?.language_name || selectedLanguage}`}</span>
      </button>
    </div>
  );
};

export default CustomTranslationNavbar;