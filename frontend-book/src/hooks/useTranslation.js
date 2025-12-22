// frontend-book/src/hooks/useTranslation.js
import { useState, useEffect } from 'react';
import translationAPI from '../services/translationAPI';

const PREFERENCE_KEY = 'book-translation-preferences';

const useTranslation = () => {
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cachedTranslations, setCachedTranslations] = useState(new Map());
  const [userPreferences, setUserPreferences] = useState(() => {
    // Load preferences from localStorage
    const saved = localStorage.getItem(PREFERENCE_KEY);
    return saved ? JSON.parse(saved) : {
      defaultTargetLanguage: 'es', // Default to Spanish
      showComparison: false,
      preferredLanguages: ['es', 'fr'] // User's preferred languages
    };
  });

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(PREFERENCE_KEY, JSON.stringify(userPreferences));
  }, [userPreferences]);

  // Load supported languages on initialization
  useEffect(() => {
    const loadSupportedLanguages = async () => {
      try {
        const languages = await translationAPI.getSupportedLanguages();
        setSupportedLanguages(languages);
      } catch (err) {
        console.error('Failed to load supported languages:', err);
        setError('Failed to load supported languages');
      }
    };

    loadSupportedLanguages();
  }, []);

  const translateText = async (text, sourceLang, targetLang, options = {}) => {
    const cacheKey = `${sourceLang}-${targetLang}:${text.substring(0, 50)}...`;

    // Check if translation is already cached
    if (cachedTranslations.has(cacheKey)) {
      return cachedTranslations.get(cacheKey);
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await translationAPI.translateContent(
        text,
        sourceLang,
        targetLang,
        options
      );

      // Cache the result
      setCachedTranslations(prev => new Map(prev.set(cacheKey, result)));
      return result;
    } catch (err) {
      console.error('Translation failed:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const translateSelection = async (fullContent, selectionStart, selectionEnd, sourceLang, targetLang) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await translationAPI.translateSelection(
        fullContent,
        selectionStart,
        selectionEnd,
        sourceLang,
        targetLang
      );

      return result;
    } catch (err) {
      console.error('Selection translation failed:', err);
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const getLanguageName = (languageCode) => {
    const language = supportedLanguages.find(lang => lang.language_code === languageCode);
    return language ? language.language_name : languageCode;
  };

  const updatePreferences = (newPreferences) => {
    setUserPreferences(prev => ({
      ...prev,
      ...newPreferences
    }));
  };

  const addPreferredLanguage = (languageCode) => {
    setUserPreferences(prev => {
      if (!prev.preferredLanguages.includes(languageCode)) {
        const newPreferred = [...prev.preferredLanguages, languageCode];
        return {
          ...prev,
          preferredLanguages: newPreferred
        };
      }
      return prev;
    });
  };

  const removePreferredLanguage = (languageCode) => {
    setUserPreferences(prev => {
      const newPreferred = prev.preferredLanguages.filter(lang => lang !== languageCode);
      return {
        ...prev,
        preferredLanguages: newPreferred
      };
    });
  };

  return {
    supportedLanguages,
    isLoading,
    error,
    translateText,
    translateSelection,
    getLanguageName,
    userPreferences,
    updatePreferences,
    addPreferredLanguage,
    removePreferredLanguage,
    cachedTranslations: Array.from(cachedTranslations.entries())
  };
};

export default useTranslation;