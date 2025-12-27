/**
 * Easy Embed Script for AI Book Chatbot
 *
 * Add to your website:
 * <script src="https://your-domain.com/js/embed.js"></script>
 *
 * Or with custom options:
 * <script>
 *   window.AI_CHAT_API_URL = 'http://localhost:8000';
 *   window.AI_CHAT_PROVIDER = 'qdrant'; // qdrant, cohere, huggingface
 *   window.AI_CHAT_COLOR = '#6366f1';
 * </script>
 * <script src="https://your-domain.com/js/embed.js"></script>
 */

// Auto-load the chatbot widget
(function() {
    'use strict';

    // Get API URL - try multiple sources
    const getApiUrl = () => {
        // 1. Check window config
        if (window.AI_CHAT_API_URL) return window.AI_CHAT_API_URL;

        // 2. Try to detect from current path
        const scripts = document.getElementsByTagName('script');
        for (let script of scripts) {
            if (script.src && script.src.includes('embed.js')) {
                // Get base URL from script src
                const url = new URL(script.src);
                return url.origin + '/api/chat';
            }
        }

        // 3. Default to current origin
        return window.location.origin + '/api/chat';
    };

    // Get provider
    const getProvider = () => {
        return window.AI_CHAT_PROVIDER || 'qdrant';
    };

    // Get color
    const getColor = () => {
        return window.AI_CHAT_COLOR || '#6366f1';
    };

    // Configuration
    window.AI_CHAT_API_URL = getApiUrl();
    window.AI_CHAT_PROVIDER = getProvider();
    window.AI_CHAT_COLOR = getColor();

    // Load the main widget
    const loadWidget = () => {
        const script = document.createElement('script');
        script.src = window.AI_CHAT_API_URL.replace('/api/chat', '/js/ai-chatbot-widget.js');
        script.async = true;
        script.onload = () => console.log('AI Chatbot loaded!');
        script.onerror = () => console.warn('AI Chatbot widget not found at expected path');
        document.body.appendChild(script);
    };

    // Load when ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadWidget);
    } else {
        loadWidget();
    }
})();
