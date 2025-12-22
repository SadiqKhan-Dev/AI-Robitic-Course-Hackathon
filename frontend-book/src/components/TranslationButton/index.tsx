import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useTranslation from '../../hooks/useTranslation';
import './styles.module.css';

interface TranslationButtonProps {
  variant?: 'icon' | 'text' | 'icon-text';
  size?: 'small' | 'medium' | 'large';
  position?: 'inline' | 'floating';
}

const TranslationButton: React.FC<TranslationButtonProps> = ({
  variant = 'icon-text',
  size = 'medium',
  position = 'inline'
}) => {
  const { siteConfig } = useDocusaurusContext();
  const { supportedLanguages, userPreferences, updatePreferences, isLoading } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(userPreferences?.defaultTargetLanguage || 'es');

  useEffect(() => {
    if (userPreferences?.defaultTargetLanguage) {
      setSelectedLanguage(userPreferences.defaultTargetLanguage);
    }
  }, [userPreferences]);

  const handleLanguageChange = (langCode: string) => {
    setSelectedLanguage(langCode);
    updatePreferences?.({ defaultTargetLanguage: langCode });
    setIsOpen(false);
  };

  const handleTranslate = () => {
    // Navigate to the docs section to see translation in action
    // In a real implementation, this would trigger the translation functionality
    window.location.href = '/docs/intro';
  };

  const languageOptions = supportedLanguages.filter(lang => lang.is_enabled);

  const sizeClasses = {
    small: 'button--sm',
    medium: 'button--md',
    large: 'button--lg'
  };

  const positionClasses = position === 'floating'
    ? 'translation-button-floating'
    : 'translation-button-inline';

  if (supportedLanguages.length === 0) {
    return (
      <div className={`translation-button-container ${positionClasses}`}>
        <button className={`button button--primary ${sizeClasses[size]}`} disabled>
          {isLoading ? 'Loading...' : 'Translate'}
        </button>
      </div>
    );
  }

  return (
    <div className={`translation-button-container ${positionClasses}`}>
      <div className="dropdown dropdown--right dropdown--bordered">
        <button
          className={`button button--primary ${sizeClasses[size]}`}
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          aria-haspopup="true"
        >
          {variant.includes('icon') && <span className="translation-icon">🌐</span>}
          {variant.includes('text') && <span>Translate</span>}
          <span className="dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
        </button>

        {isOpen && (
          <ul className="dropdown__menu">
            {languageOptions.map((lang) => (
              <li key={lang.language_code}>
                <a
                  className={`dropdown__link ${selectedLanguage === lang.language_code ? 'dropdown__link--active' : ''}`}
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handleLanguageChange(lang.language_code);
                  }}
                >
                  {lang.language_name} ({lang.language_code.toUpperCase()})
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>

      <button
        className={`button button--secondary ${sizeClasses[size]}`}
        onClick={handleTranslate}
        disabled={isLoading}
      >
        {isLoading ? 'Translating...' : `To ${supportedLanguages.find(lang => lang.language_code === selectedLanguage)?.language_name || selectedLanguage}`}
      </button>
    </div>
  );
};

export default TranslationButton;