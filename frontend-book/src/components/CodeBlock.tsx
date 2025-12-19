import React, { useState } from 'react';
import clsx from 'clsx';
import Highlight, { defaultProps, Language } from 'prism-react-renderer';

type CodeBlockProps = {
  children: string;
  className?: string;
  title?: string;
  showLineNumbers?: boolean;
};

const CodeBlock: React.FC<CodeBlockProps> = ({ 
  children, 
  className = '', 
  title,
  showLineNumbers = false 
}) => {
  const [isCopied, setIsCopied] = useState(false);
  const language = className.replace(/language-/, '') as Language;

  const code = children.trim();

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    });
  };

  return (
    <div className={clsx('code-block-wrapper', 'shadow--md', className)}>
      {title && (
        <div className="code-block-title">
          {title}
        </div>
      )}
      <div className="code-block-content">
        <Highlight 
          {...defaultProps} 
          code={code} 
          language={language || 'javascript'}
          theme={undefined}
        >
          {({ className, style, tokens, getLineProps, getTokenProps }) => (
            <pre className={className} style={style}>
              <button 
                onClick={copyToClipboard}
                className="code-block-copy-button"
                aria-label="Copy code to clipboard"
              >
                {isCopied ? '✓ Copied!' : 'Copy'}
              </button>
              <code>
                {tokens.map((line, i) => (
                  <div key={i} {...getLineProps({ line, key: i })}>
                    {showLineNumbers && (
                      <span className="code-block-line-number">
                        {i + 1}
                      </span>
                    )}
                    {line.map((token, key) => (
                      <span key={key} {...getTokenProps({ token })} />
                    ))}
                  </div>
                ))}
              </code>
            </pre>
          )}
        </Highlight>
      </div>
    </div>
  );
};

export default CodeBlock;