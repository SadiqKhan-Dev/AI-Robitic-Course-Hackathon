import React from 'react';
import Layout from '@theme/Layout';
import FloatingRAGAgent from '../components/FloatingRAGAgent';

// Layout wrapper that adds the floating RAG agent to all pages
export default function LayoutWrapper(props) {
  return (
    <Layout {...props}>
      {props.children}
      <FloatingRAGAgent />
    </Layout>
  );
}