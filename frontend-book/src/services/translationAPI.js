// frontend-book/src/services/translationAPI.js
// Use Docusaurus environment variable pattern
const getAPIBaseUrl = () => {
  // Check if we're in the browser environment
  if (typeof window !== 'undefined') {
    // Client-side: use appropriate base URL
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      // Default backend URL for local development
      return 'http://localhost:8000/api/v1';
    } else {
      // For production, use the same origin
      return `${window.location.origin}/api/v1`;
    }
  }
  // Server-side (SSR) fallback for build process
  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getAPIBaseUrl();

class TranslationAPI {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async getSupportedLanguages() {
    try {
      const response = await fetch(`${this.baseUrl}/supported-languages`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.languages;
    } catch (error) {
      console.error('Error fetching supported languages:', error);
      throw error;
    }
  }

  async translateContent(sourceContent, sourceLanguage, targetLanguage, options = {}) {
    const {
      preserveFormatting = true,
      preserveCodeBlocks = true,
      preserveTechnicalTerms = true
    } = options;

    try {
      const response = await fetch(`${this.baseUrl}/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_content: sourceContent,
          source_language: sourceLanguage,
          target_language: targetLanguage,
          preserve_formatting: preserveFormatting,
          preserve_code_blocks: preserveCodeBlocks,
          preserve_technical_terms: preserveTechnicalTerms
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error translating content:', error);
      throw error;
    }
  }

  async translateSelection(fullContent, selectionStart, selectionEnd, sourceLanguage, targetLanguage) {
    try {
      const response = await fetch(`${this.baseUrl}/translate-selection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          full_content: fullContent,
          selection_start: selectionStart,
          selection_end: selectionEnd,
          source_language: sourceLanguage,
          target_language: targetLanguage
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error translating selection:', error);
      throw error;
    }
  }
}

export default new TranslationAPI();