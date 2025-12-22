import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import { TranslationProvider } from '../components/TranslationProvider';

// This wraps the original Docusaurus Layout component with our TranslationProvider
const Layout = (props) => {
  return (
    <TranslationProvider>
      <OriginalLayout {...props} />
    </TranslationProvider>
  );
};

export default Layout;