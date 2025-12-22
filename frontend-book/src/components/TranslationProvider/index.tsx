import React, { createContext, useContext, ReactNode } from 'react';
import { useTranslation } from '../hooks/useTranslation';

interface TranslationContextType {
  supportedLanguages: any[];
  userPreferences: any;
  updatePreferences: (prefs: any) => void;
  isLoading: boolean;
  error: string | null;
  translateText: (text: string, sourceLang: string, targetLang: string, options?: any) => Promise<any>;
  translateSelection: (fullContent: string, selectionStart: number, selectionEnd: number, sourceLang: string, targetLang: string) => Promise<any>;
  getLanguageName: (languageCode: string) => string;
}

const TranslationContext = createContext<TranslationContextType | undefined>(undefined);

export const TranslationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const translationHook = useTranslation();

  return (
    <TranslationContext.Provider value={translationHook}>
      {children}
    </TranslationContext.Provider>
  );
};

export const useTranslationContext = (): TranslationContextType => {
  const context = useContext(TranslationContext);
  if (context === undefined) {
    throw new Error('useTranslationContext must be used within a TranslationProvider');
  }
  return context;
};