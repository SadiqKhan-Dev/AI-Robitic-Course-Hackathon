// Simple mock translation service for testing purposes
// In a real implementation, this would connect to the actual translation API

const mockTranslations = {
  "Hello, world!": {
    "ur": "ہیلو، دنیا!",
    "es": "¡Hola, mundo!",
    "fr": "Bonjour le monde !",
    "ar": "!مرحبا بالعالم"
  },
  "Welcome to the robotics course": {
    "ur": "روبوٹکس کورس میں خوش آمدید",
    "es": "Bienvenido al curso de robótica",
    "fr": "Bienvenue dans le cours de robotique",
    "ar": "مرحبا بكم في دورة الروبوتات"
  }
};

export const mockTranslate = (text, sourceLang, targetLang) => {
  // Simple word-for-word translation for demo purposes
  // In reality, this would call the backend API
  
  // Check if we have a mock translation
  if (mockTranslations[text] && mockTranslations[text][targetLang]) {
    return mockTranslations[text][targetLang];
  }
  
  // For demo purposes, return the text with a note
  return `${text} [Translated to ${targetLang}]`;
};