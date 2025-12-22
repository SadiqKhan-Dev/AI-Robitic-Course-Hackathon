import React, { useState, useEffect, useRef } from 'react';
import './TranslatedContent.css';

const TranslatedContent = ({
  originalContent,
  translatedContent,
  targetLanguage,
  showOriginal = false,
  onContentChange,
  error = null,
  showTechnicalMarkers = true,
  qualityScore = null,
  onSelectionTranslate
}) => {
  const [displayContent, setDisplayContent] = useState(originalContent);
  const [isTranslated, setIsTranslated] = useState(false);
  const [technicalElements, setTechnicalElements] = useState([]);
  const [selectionInfo, setSelectionInfo] = useState(null);
  const contentRef = useRef(null);

  useEffect(() => {
    if (error) {
      // If there's an error, show the original content with an error message
      setDisplayContent(originalContent);
      setIsTranslated(false);
    } else if (translatedContent && !showOriginal) {
      setDisplayContent(translatedContent);
      setIsTranslated(true);
    } else {
      setDisplayContent(originalContent);
      setIsTranslated(false);
    }
  }, [originalContent, translatedContent, showOriginal, error]);

  // Extract and track technical elements
  useEffect(() => {
    if (displayContent) {
      const elements = extractTechnicalElements(displayContent);
      setTechnicalElements(elements);
    }
  }, [displayContent]);

  // Update parent when content changes
  useEffect(() => {
    if (onContentChange) {
      onContentChange(displayContent, isTranslated, error, technicalElements);
    }
  }, [displayContent, isTranslated, error, technicalElements, onContentChange]);

  // Set up text selection handling
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      if (selection.toString().trim() !== '' && contentRef.current && contentRef.current.contains(selection.anchorNode)) {
        const range = selection.getRangeAt(0);
        const preSelectionRange = range.cloneRange();
        preSelectionRange.selectNodeContents(contentRef.current);
        preSelectionRange.setEnd(range.startContainer, range.startOffset);
        const start = preSelectionRange.toString().length;
        const end = start + range.toString().length;

        setSelectionInfo({
          text: selection.toString(),
          start: start,
          end: end,
          range: range
        });
      } else {
        setSelectionInfo(null);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
    };
  }, []);

  // Function to extract technical elements from content
  const extractTechnicalElements = (content) => {
    if (!content) return [];

    const elements = [];

    // Extract code blocks (```...``` and `...`)
    const codeBlockRegex = /(```[\s\S]*?```|`[^`\n]*`)/g;
    let match;
    while ((match = codeBlockRegex.exec(content)) !== null) {
      elements.push({
        type: 'code',
        content: match[0],
        index: match.index
      });
    }

    // Extract file paths
    const filePathRegex = /(\/[\w\-_/\\]+(?:\.[\w]+)+)/g;
    while ((match = filePathRegex.exec(content)) !== null) {
      elements.push({
        type: 'file',
        content: match[0],
        index: match.index
      });
    }

    return elements;
  };

  const toggleDisplay = () => {
    if (translatedContent && !error) {
      const newDisplayContent = isTranslated ? originalContent : translatedContent;
      setDisplayContent(newDisplayContent);
      setIsTranslated(!isTranslated);
    }
  };

  const handleSelectionTranslate = () => {
    if (selectionInfo && onSelectionTranslate) {
      onSelectionTranslate(
        originalContent,
        selectionInfo.start,
        selectionInfo.end,
        'en', // source language
        targetLanguage || 'es' // target language
      );
    }
  };

  // Function to render content with technical markers if enabled
  const renderContentWithMarkers = (content) => {
    if (!showTechnicalMarkers || !content) {
      return <div ref={contentRef}>{content}</div>;
    }

    // For now, just return the content as is with ref
    // In a full implementation, we would add visual markers for technical elements
    return <div ref={contentRef}>{content}</div>;
  };

  // Function to render quality indicator
  const renderQualityIndicator = () => {
    if (qualityScore === null || qualityScore === undefined) return null;

    let qualityColor = '#dc3545'; // Red for low quality
    if (qualityScore >= 80) {
      qualityColor = '#28a745'; // Green for high quality
    } else if (qualityScore >= 60) {
      qualityColor = '#ffc107'; // Yellow for medium quality
    }

    return (
      <div className="quality-indicator" style={{ color: qualityColor }}>
        <span className="quality-label">Quality:</span>
        <span className="quality-score">{qualityScore}%</span>
      </div>
    );
  };

  // Function to render selection controls
  const renderSelectionControls = () => {
    if (!selectionInfo) return null;

    return (
      <div className="selection-controls">
        <button
          className="selection-translate-btn"
          onClick={handleSelectionTranslate}
          title="Translate selected text"
        >
          🌐 Translate Selection
        </button>
        <span className="selection-info">
          {selectionInfo.text.substring(0, 30)}{selectionInfo.text.length > 30 ? '...' : ''}
        </span>
      </div>
    );
  };

  return (
    <div className="translated-content-container">
      <div className={`content-display ${isTranslated ? 'translated' : 'original'} ${error ? 'error' : ''}`}>
        {targetLanguage && !error && (
          <div className="content-header">
            <span className="language-indicator">
              {isTranslated ? `Translated to ${targetLanguage.toUpperCase()}` : 'Original Content'}
            </span>
            <div className="header-controls">
              {translatedContent && (
                <button className="toggle-view-btn" onClick={toggleDisplay}>
                  {isTranslated ? 'Show Original' : 'Show Translation'}
                </button>
              )}
              {showTechnicalMarkers && (
                <span className="technical-count">
                  {technicalElements.length} technical elements
                </span>
              )}
              {isTranslated && qualityScore !== null && renderQualityIndicator()}
            </div>
          </div>
        )}
        {error && (
          <div className="error-header">
            <span className="error-indicator">⚠️ Translation Error</span>
            <p className="error-message">{error}</p>
          </div>
        )}
        {selectionInfo && renderSelectionControls()}
        <div className="content-body">
          {error ? (
            <div>
              <p>Translation failed. Showing original content:</p>
              <div ref={contentRef}>{originalContent}</div>
            </div>
          ) : (
            renderContentWithMarkers(displayContent)
          )}
        </div>
      </div>
    </div>
  );
};

export default TranslatedContent;