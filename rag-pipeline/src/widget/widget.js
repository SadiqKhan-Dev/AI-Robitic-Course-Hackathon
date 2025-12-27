/**
 * AI Book Chatbot Widget
 * Embeddable popup chatbot for websites
 *
 * Usage:
 * <script src="https://your-api.com/widget.js" data-api-url="http://localhost:8000"></script>
 */

(function() {
    'use strict';

    // Configuration
    const API_URL = window.AI_BOOK_API_URL || 'http://localhost:8000';
    const WIDGET_ID = 'ai-book-chatbot-widget';

    // Create styles
    const createStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            #${WIDGET_ID} {
                --primary-color: #6366f1;
                --primary-hover: #4f46e5;
                --text-color: #1f2937;
                --bg-color: #ffffff;
                --secondary-bg: #f3f4f6;
                --border-color: #e5e7eb;
                --user-msg-bg: #6366f1;
                --bot-msg-bg: #f3f4f6;
                --shadow: 0 10px 40px rgba(0,0,0,0.15);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                z-index: 999999;
            }

            #${WIDGET_ID} * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            /* Launcher Button */
            #${WIDGET_ID} .launcher {
                position: fixed;
                bottom: 24px;
                right: 24px;
                width: 64px;
                height: 64px;
                border-radius: 50%;
                background: var(--primary-color);
                box-shadow: var(--shadow);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.3s ease, background 0.3s ease;
                z-index: 999999;
            }

            #${WIDGET_ID} .launcher:hover {
                transform: scale(1.05);
                background: var(--primary-hover);
            }

            #${WIDGET_ID} .launcher svg {
                width: 28px;
                height: 28px;
                fill: white;
            }

            #${WIDGET_ID} .launcher .close-icon {
                display: none;
            }

            #${WIDGET_ID}.open .launcher .chat-icon {
                display: none;
            }

            #${WIDGET_ID}.open .launcher .close-icon {
                display: block;
            }

            /* Chat Window */
            #${WIDGET_ID} .chat-window {
                position: fixed;
                bottom: 100px;
                right: 24px;
                width: 400px;
                max-width: calc(100vw - 48px);
                height: 600px;
                max-height: calc(100vh - 120px);
                background: var(--bg-color);
                border-radius: 16px;
                box-shadow: var(--shadow);
                display: none;
                flex-direction: column;
                overflow: hidden;
                z-index: 999999;
            }

            #${WIDGET_ID}.open .chat-window {
                display: flex;
                animation: slideIn 0.3s ease;
            }

            @keyframes slideIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* Header */
            #${WIDGET_ID} .chat-header {
                background: var(--primary-color);
                color: white;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            #${WIDGET_ID} .bot-avatar {
                width: 40px;
                height: 40px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            #${WIDGET_ID} .bot-avatar svg {
                width: 24px;
                height: 24px;
                fill: white;
            }

            #${WIDGET_ID} .header-info h3 {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 2px;
            }

            #${WIDGET_ID} .header-info p {
                font-size: 12px;
                opacity: 0.9;
            }

            /* Messages Area */
            #${WIDGET_ID} .messages-container {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                background: var(--secondary-bg);
            }

            #${WIDGET_ID} .message {
                margin-bottom: 12px;
                max-width: 85%;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            #${WIDGET_ID} .message.user {
                margin-left: auto;
            }

            #${WIDGET_ID} .message-content {
                padding: 12px 16px;
                border-radius: 16px;
                font-size: 14px;
                line-height: 1.5;
            }

            #${WIDGET_ID} .message.bot .message-content {
                background: var(--bot-msg-bg);
                color: var(--text-color);
                border-bottom-left-radius: 4px;
            }

            #${WIDGET_ID} .message.user .message-content {
                background: var(--user-msg-bg);
                color: white;
                border-bottom-right-radius: 4px;
            }

            #${WIDGET_ID} .sources {
                margin-top: 8px;
                font-size: 11px;
                color: #6b7280;
            }

            #${WIDGET_ID} .sources a {
                color: var(--primary-color);
                text-decoration: none;
            }

            /* Typing Indicator */
            #${WIDGET_ID} .typing-indicator {
                display: none;
                padding: 12px 16px;
                background: var(--bot-msg-bg);
                border-radius: 16px;
                border-bottom-left-radius: 4px;
                width: fit-content;
                margin-bottom: 12px;
            }

            #${WIDGET_ID} .typing-indicator span {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #9ca3af;
                border-radius: 50%;
                margin: 0 2px;
                animation: bounce 1.4s infinite ease-in-out;
            }

            #${WIDGET_ID} .typing-indicator span:nth-child(1) { animation-delay: 0s; }
            #${WIDGET_ID} .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
            #${WIDGET_ID} .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

            @keyframes bounce {
                0%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-8px); }
            }

            /* Input Area */
            #${WIDGET_ID} .input-area {
                padding: 16px;
                background: var(--bg-color);
                border-top: 1px solid var(--border-color);
                display: flex;
                gap: 8px;
            }

            #${WIDGET_ID} .input-area input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid var(--border-color);
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }

            #${WIDGET_ID} .input-area input:focus {
                border-color: var(--primary-color);
            }

            #${WIDGET_ID} .input-area button {
                width: 44px;
                height: 44px;
                border: none;
                border-radius: 50%;
                background: var(--primary-color);
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.3s;
            }

            #${WIDGET_ID} .input-area button:hover {
                background: var(--primary-hover);
            }

            #${WIDGET_ID} .input-area button:disabled {
                background: #9ca3af;
                cursor: not-allowed;
            }

            #${WIDGET_ID} .input-area button svg {
                width: 20px;
                height: 20px;
                fill: currentColor;
            }

            /* Welcome Message */
            #${WIDGET_ID} .welcome-message {
                text-align: center;
                padding: 32px 16px;
                color: #6b7280;
            }

            #${WIDGET_ID} .welcome-message h4 {
                color: var(--text-color);
                margin-bottom: 8px;
            }

            #${WIDGET_ID} .suggestions {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: center;
                margin-top: 16px;
            }

            #${WIDGET_ID} .suggestion-chip {
                padding: 8px 16px;
                background: var(--primary-color);
                color: white;
                border-radius: 20px;
                font-size: 13px;
                cursor: pointer;
                transition: opacity 0.3s;
            }

            #${WIDGET_ID} .suggestion-chip:hover {
                opacity: 0.9;
            }

            /* Error Message */
            #${WIDGET_ID} .error-message {
                background: #fee2e2;
                color: #dc2626;
                padding: 12px 16px;
                border-radius: 8px;
                margin: 12px;
                font-size: 14px;
            }

            /* Responsive */
            @media (max-width: 480px) {
                #${WIDGET_ID} .chat-window {
                    width: calc(100vw - 16px);
                    right: 8px;
                    bottom: 90px;
                    height: calc(100vh - 100px);
                }

                #${WIDGET_ID} .launcher {
                    width: 56px;
                    height: 56px;
                    bottom: 16px;
                    right: 16px;
                }
            }
        `;
        document.head.appendChild(style);
    };

    // Create widget HTML
    const createWidget = () => {
        const widget = document.createElement('div');
        widget.id = WIDGET_ID;
        widget.innerHTML = `
            <button class="launcher" aria-label="Open chat">
                <svg class="chat-icon" viewBox="0 0 24 24">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
                <svg class="close-icon" viewBox="0 0 24 24">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>
            <div class="chat-window">
                <div class="chat-header">
                    <div class="bot-avatar">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    <div class="header-info">
                        <h3>AI Book Assistant</h3>
                        <p>Ask me about the AI Robotics Book</p>
                    </div>
                </div>
                <div class="messages-container">
                    <div class="welcome-message">
                        <h4>Welcome! 👋</h4>
                        <p>I can answer questions about the AI Robotics Book using the embedded knowledge base.</p>
                        <div class="suggestions">
                            <span class="suggestion-chip" data-message="What is VLA pipeline?">What is VLA?</span>
                            <span class="suggestion-chip" data-message="Explain autonomous humanoid">Autonomous Humanoid</span>
                            <span class="suggestion-chip" data-message="How does LLM planning work?">LLM Planning</span>
                        </div>
                    </div>
                </div>
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
                <div class="input-area">
                    <input type="text" placeholder="Ask a question..." autocomplete="off">
                    <button type="button" aria-label="Send message">
                        <svg viewBox="0 0 24 24">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(widget);
        return widget;
    };

    // Chatbot class
    class Chatbot {
        constructor() {
            this.widget = document.getElementById(WIDGET_ID);
            this.messagesContainer = this.widget.querySelector('.messages-container');
            this.typingIndicator = this.widget.querySelector('.typing-indicator');
            this.input = this.widget.querySelector('.input-area input');
            this.sendButton = this.widget.querySelector('.input-area button');
            this.launcher = this.widget.querySelector('.launcher');

            this.init();
        }

        init() {
            // Toggle chat
            this.launcher.addEventListener('click', () => this.toggle());

            // Send message
            this.sendButton.addEventListener('click', () => this.send());
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.send();
            });

            // Suggestion chips
            this.widget.querySelectorAll('.suggestion-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    this.input.value = chip.dataset.message;
                    this.send();
                });
            });

            // Remove welcome message when first message is sent
            this.welcomeMessage = this.widget.querySelector('.welcome-message');
        }

        toggle() {
            this.widget.classList.toggle('open');
            if (this.widget.classList.contains('open')) {
                this.input.focus();
            }
        }

        async send() {
            const message = this.input.value.trim();
            if (!message) return;

            // Remove welcome message
            if (this.welcomeMessage) {
                this.welcomeMessage.remove();
                this.welcomeMessage = null;
            }

            // Add user message
            this.addMessage(message, 'user');
            this.input.value = '';

            // Show typing indicator
            this.typingIndicator.style.display = 'block';
            this.messagesContainer.appendChild(this.typingIndicator);
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            this.sendButton.disabled = true;

            try {
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message }),
                });

                const data = await response.json();

                // Hide typing indicator
                this.typingIndicator.style.display = 'none';

                if (data.success) {
                    this.addMessage(data.answer, 'bot', data.sources);
                } else {
                    this.addMessage(data.error || 'Sorry, something went wrong.', 'bot');
                }
            } catch (error) {
                this.typingIndicator.style.display = 'none';
                this.addMessage('Sorry, I couldn\'t connect to the server. Please try again.', 'bot');
            }

            this.sendButton.disabled = false;
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }

        addMessage(content, role, sources = []) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;

            let html = `<div class="message-content">${this.escapeHtml(content)}</div>`;

            if (sources && sources.length > 0) {
                html += '<div class="sources">';
                sources.forEach((source, i) => {
                    if (source.title) {
                        html += `<a href="${source.url || '#'}" target="_blank">📄 ${source.title}</a>`;
                        if (i < sources.length - 1) html += ' • ';
                    }
                });
                html += '</div>';
            }

            messageDiv.innerHTML = html;
            this.messagesContainer.appendChild(messageDiv);
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    // Initialize
    const init = () => {
        createStyles();
        createWidget();
        new Chatbot();
    };

    // Load when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
