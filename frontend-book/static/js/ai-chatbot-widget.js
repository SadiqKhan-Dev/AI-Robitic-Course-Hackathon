/**
 * AI Book Chatbot Widget
 * Multi-Provider RAG Support: Qdrant, Cohere, HuggingFace
 *
 * Embed in your Docusaurus website:
 * <script src="/js/ai-chatbot-widget.js" data-provider="qdrant"></script>
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        apiUrl: window.AI_CHAT_API_URL || '/api/chat',
        provider: window.AI_CHAT_PROVIDER || 'qdrant',
        title: window.AI_CHAT_TITLE || 'AI Book Assistant',
        subtitle: window.AI_CHAT_SUBTITLE || 'Ask me about the AI Robotics Book',
        primaryColor: window.AI_CHAT_COLOR || '#6366f1',
        position: window.AI_CHAT_POSITION || 'bottom-right'  // bottom-right, bottom-left
    };

    const WIDGET_ID = 'ai-book-chatbot';

    // Provider configurations
    const PROVIDERS = {
        qdrant: {
            name: 'Qdrant Vector DB',
            description: 'Fast vector search with cosine similarity',
            icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>'
        },
        cohere: {
            name: 'Cohere Embeddings',
            description: 'State-of-the-art embeddings',
            icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>'
        },
        huggingface: {
            name: 'HuggingFace Inference',
            description: 'Open source ML models',
            icon: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>'
        }
    };

    // Create styles
    const createStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            #${WIDGET_ID} {
                --primary: ${CONFIG.primaryColor};
                --primary-dark: ${CONFIG.primaryColor}dd;
                --text: #1f2937;
                --bg: #ffffff;
                --secondary-bg: #f9fafb;
                --border: #e5e7eb;
                --user-msg: ${CONFIG.primaryColor};
                --bot-msg: ${CONFIG.secondary-bg};
                --shadow: 0 4px 24px rgba(0,0,0,0.12);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                z-index: 999999;
            }

            #${WIDGET_ID} * { box-sizing: border-box; margin: 0; padding: 0; }

            /* Launcher */
            #${WIDGET_ID} .launcher {
                position: fixed;
                ${CONFIG.position.includes('right') ? 'right: 24px' : 'left: 24px'}: 24px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: var(--primary);
                box-shadow: var(--shadow);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                z-index: 999999;
                border: none;
            }

            #${WIDGET_ID} .launcher:hover {
                transform: scale(1.08);
                box-shadow: 0 8px 32px rgba(0,0,0,0.16);
            }

            #${WIDGET_ID} .launcher svg {
                width: 28px;
                height: 28px;
                fill: white;
            }

            #${WIDGET_ID} .launcher .close { display: none; }
            #${WIDGET_ID}.open .launcher .chat { display: none; }
            #${WIDGET_ID}.open .launcher .close { display: block; }

            /* Chat Window */
            #${WIDGET_ID} .chat-window {
                position: fixed;
                ${CONFIG.position.includes('right') ? 'right' : 'left'}: 24px;
                bottom: 100px;
                width: 420px;
                max-width: calc(100vw - 48px);
                height: 580px;
                max-height: calc(100vh - 140px);
                background: var(--bg);
                border-radius: 20px;
                box-shadow: var(--shadow);
                display: none;
                flex-direction: column;
                overflow: hidden;
                z-index: 999999;
                border: 1px solid var(--border);
            }

            #${WIDGET_ID}.open .chat-window {
                display: flex;
                animation: slideUp 0.3s ease;
            }

            @keyframes slideUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* Header */
            #${WIDGET_ID} .chat-header {
                background: linear-gradient(135deg, var(--primary), var(--primary-dark));
                color: white;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 14px;
            }

            #${WIDGET_ID} .bot-avatar {
                width: 48px;
                height: 48px;
                background: rgba(255,255,255,0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            #${WIDGET_ID} .bot-avatar svg {
                width: 28px;
                height: 28px;
                fill: white;
            }

            #${WIDGET_ID} .header-info h3 {
                font-size: 17px;
                font-weight: 600;
            }

            #${WIDGET_ID} .header-info p {
                font-size: 12px;
                opacity: 0.9;
                display: flex;
                align-items: center;
                gap: 6px;
            }

            #${WIDGET_ID} .provider-badge {
                background: rgba(255,255,255,0.2);
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
            }

            /* Messages */
            #${WIDGET_ID} .messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: var(--secondary-bg);
            }

            #${WIDGET_ID} .message {
                margin-bottom: 14px;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

            #${WIDGET_ID} .message.user { margin-left: auto; max-width: 85%; }

            #${WIDGET_ID} .msg-content {
                padding: 14px 18px;
                border-radius: 18px;
                font-size: 14.5px;
                line-height: 1.6;
            }

            #${WIDGET_ID} .message.bot .msg-content {
                background: var(--bot-msg);
                color: var(--text);
                border-bottom-left-radius: 4px;
            }

            #${WIDGET_ID} .message.user .msg-content {
                background: var(--user-msg);
                color: white;
                border-bottom-right-radius: 4px;
            }

            /* Sources */
            #${WIDGET_ID} .sources {
                margin-top: 10px;
                padding: 10px 14px;
                background: rgba(99, 102, 241, 0.08);
                border-radius: 10px;
                font-size: 12px;
            }

            #${WIDGET_ID} .sources-title {
                font-weight: 600;
                color: var(--primary);
                margin-bottom: 6px;
            }

            #${WIDGET_ID} .sources a {
                color: var(--primary);
                text-decoration: none;
                display: block;
                padding: 4px 0;
            }

            #${WIDGET_ID} .sources a:hover { text-decoration: underline; }

            /* Typing */
            #${WIDGET_ID} .typing {
                display: none;
                padding: 14px 18px;
                background: var(--bot-msg);
                border-radius: 18px;
                border-bottom-left-radius: 4px;
                width: fit-content;
                margin-bottom: 14px;
            }

            #${WIDGET_ID} .typing span {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #9ca3af;
                border-radius: 50%;
                margin: 0 2px;
                animation: bounce 1.4s infinite ease-in-out;
            }

            #${WIDGET_ID} .typing span:nth-child(1) { animation-delay: 0s; }
            #${WIDGET_ID} .typing span:nth-child(2) { animation-delay: 0.2s; }
            #${WIDGET_ID} .typing span:nth-child(3) { animation-delay: 0.4s; }

            @keyframes bounce {
                0%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-6px); }
            }

            /* Input */
            #${WIDGET_ID} .input-area {
                padding: 16px 20px;
                background: var(--bg);
                border-top: 1px solid var(--border);
                display: flex;
                gap: 10px;
            }

            #${WIDGET_ID} .input-area input {
                flex: 1;
                padding: 14px 18px;
                border: 1px solid var(--border);
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: all 0.3s;
            }

            #${WIDGET_ID} .input-area input:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            }

            #${WIDGET_ID} .input-area button {
                width: 48px;
                height: 48px;
                border: none;
                border-radius: 50%;
                background: var(--primary);
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
            }

            #${WIDGET_ID} .input-area button:hover {
                background: var(--primary-dark);
            }

            #${WIDGET_ID} .input-area button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            #${WIDGET_ID} .input-area button svg {
                width: 20px;
                height: 20px;
                fill: currentColor;
            }

            /* Welcome */
            #${WIDGET_ID} .welcome {
                text-align: center;
                padding: 30px 20px;
                color: #6b7280;
            }

            #${WIDGET_ID} .welcome h4 {
                color: var(--text);
                font-size: 16px;
                margin-bottom: 8px;
            }

            #${WIDGET_ID} .suggestions {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: center;
                margin-top: 20px;
            }

            #${WIDGET_ID} .chip {
                padding: 8px 16px;
                background: var(--primary);
                color: white;
                border-radius: 20px;
                font-size: 13px;
                cursor: pointer;
                transition: all 0.3s;
            }

            #${WIDGET_ID} .chip:hover {
                opacity: 0.9;
                transform: translateY(-1px);
            }

            /* Provider info in sidebar */
            #${WIDGET_ID} .provider-info {
                padding: 12px 20px;
                background: rgba(99, 102, 241, 0.08);
                font-size: 11px;
                color: #6b7280;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            #${WIDGET_ID} .provider-info svg {
                width: 16px;
                height: 16px;
                fill: var(--primary);
            }

            /* Responsive */
            @media (max-width: 500px) {
                #${WIDGET_ID} .chat-window {
                    width: calc(100vw - 16px);
                    ${CONFIG.position.includes('right') ? 'right' : 'left'}: 8px;
                    bottom: 90px;
                    height: calc(100vh - 110px);
                }

                #${WIDGET_ID} .launcher {
                    width: 52px;
                    height: 52px;
                    bottom: 16px;
                    ${CONFIG.position.includes('right') ? 'right' : 'left'}: 16px;
                }
            }
        `;
        document.head.appendChild(style);
    };

    // Create widget HTML
    const createWidget = () => {
        const provider = PROVIDERS[CONFIG.provider] || PROVIDERS.qdrant;

        const widget = document.createElement('div');
        widget.id = WIDGET_ID;
        widget.innerHTML = `
            <button class="launcher" aria-label="Open chat">
                <svg class="chat" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
                <svg class="close" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
            <div class="chat-window">
                <div class="chat-header">
                    <div class="bot-avatar">${provider.icon}</div>
                    <div class="header-info">
                        <h3>${CONFIG.title}</h3>
                        <p><span class="provider-badge">${provider.name}</span></p>
                    </div>
                </div>
                <div class="provider-info">
                    ${provider.icon}
                    <span>${provider.description}</span>
                </div>
                <div class="messages">
                    <div class="welcome">
                        <h4>Welcome! 👋</h4>
                        <p>Ask me anything about the AI Robotics Book. I use ${provider.name} for intelligent answers.</p>
                        <div class="suggestions">
                            <span class="chip" data-msg="What is the VLA pipeline?">VLA Pipeline</span>
                            <span class="chip" data-msg="Explain autonomous humanoid">Autonomous Humanoid</span>
                            <span class="chip" data-msg="How does LLM planning work?">LLM Planning</span>
                        </div>
                    </div>
                </div>
                <div class="typing"><span></span><span></span><span></span></div>
                <div class="input-area">
                    <input type="text" placeholder="Type your question..." autocomplete="off">
                    <button aria-label="Send">
                        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
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
            this.messages = this.widget.querySelector('.messages');
            this.typing = this.widget.querySelector('.typing');
            this.input = this.widget.querySelector('.input-area input');
            this.btn = this.widget.querySelector('.input-area button');
            this.launcher = this.widget.querySelector('.launcher');
            this.welcome = this.widget.querySelector('.welcome');
            this.init();
        }

        init() {
            this.launcher.addEventListener('click', () => this.toggle());
            this.btn.addEventListener('click', () => this.send());
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.send();
            });
            this.widget.querySelectorAll('.chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    this.input.value = chip.dataset.msg;
                    this.send();
                });
            });
        }

        toggle() {
            this.widget.classList.toggle('open');
            if (this.widget.classList.contains('open')) {
                setTimeout(() => this.input.focus(), 100);
            }
        }

        async send() {
            const msg = this.input.value.trim();
            if (!msg) return;

            if (this.welcome) {
                this.welcome.remove();
                this.welcome = null;
            }

            this.addMessage(msg, 'user');
            this.input.value = '';
            this.btn.disabled = true;

            this.typing.style.display = 'block';
            this.messages.appendChild(this.typing);
            this.messages.scrollTop = this.messages.scrollHeight;

            try {
                const res = await fetch(CONFIG.apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, provider: CONFIG.provider })
                });
                const data = await res.json();
                this.typing.style.display = 'none';

                if (data.success) {
                    this.addMessage(data.answer, 'bot', data.sources);
                } else {
                    this.addMessage(data.error || 'Sorry, I couldn\'t help with that.', 'bot');
                }
            } catch (e) {
                this.typing.style.display = 'none';
                this.addMessage('Connection error. Please check your server.', 'bot');
            }

            this.btn.disabled = false;
            this.messages.scrollTop = this.messages.scrollHeight;
        }

        addMessage(text, role, sources = []) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            let html = `<div class="msg-content">${this.escape(text)}</div>`;

            if (sources && sources.length > 0) {
                html += '<div class="sources"><div class="sources-title">📚 Sources:</div>';
                sources.forEach(s => {
                    if (s.title) {
                        html += `<a href="${s.url || '#'}" target="_blank">• ${s.title}</a>`;
                    }
                });
                html += '</div>';
            }

            div.innerHTML = html;
            this.messages.appendChild(div);
        }

        escape(text) {
            const d = document.createElement('div');
            d.textContent = text;
            return d.innerHTML;
        }
    }

    // Initialize
    const init = () => {
        createStyles();
        createWidget();
        new Chatbot();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
