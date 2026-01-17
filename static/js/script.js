document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatHistory = document.getElementById('chat-history');
    const sendBtn = document.getElementById('send-btn');
    const clearBtn = document.getElementById('clear-btn');

    // Enable/disable send button
    userInput.addEventListener('input', () => {
        sendBtn.disabled = !userInput.value.trim();
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to UI
        appendMessage('user', message);
        userInput.value = '';
        sendBtn.disabled = true;

        // Add typing indicator
        const loadingId = appendLoading();
        scrollToBottom();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Remove loading indicator
            removeLoading(loadingId);

            if (!response.ok) {
                appendMessage('bot', `Error: ${data.detail || 'Something went wrong'}`);
            } else {
                // If there are specific recommendations, format them nicely
                if (data.recommendations && data.recommendations.length > 0) {
                    const fragment = document.createDocumentFragment();
                    
                    // Intro message if present
                    if (data.message) {
                        const p = document.createElement('p');
                        p.textContent = data.message;
                        p.style.marginBottom = '1rem';
                        fragment.appendChild(p);
                    }

                    // Render recommendations
                    data.recommendations.forEach(rec => {
                        const card = document.createElement('div');
                        card.className = 'recommendation-card';
                        card.innerHTML = `
                            <div class="rec-title">${rec.title}</div>
                            <div class="rec-meta">
                                <span>${rec.genres}</span>
                                <span>⭐ ${rec.rating.toFixed(1)}</span>
                            </div>
                            <div class="rec-explanation">${rec.explanation}</div>
                        `;
                        fragment.appendChild(card);
                    });

                    appendMessage('bot', fragment);
                } else {
                    // Just a text response
                    appendMessage('bot', data.message || "I couldn't generate a response.");
                }
            }
        } catch (error) {
            removeLoading(loadingId);
            appendMessage('bot', "Sorry, I'm having trouble connecting to the server.");
            console.error(error);
        }
        
        scrollToBottom();
    });

    clearBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the conversation history?')) {
            try {
                await fetch('/clear', { method: 'POST' });
                // clear UI except system message
                const systemMessage = chatHistory.querySelector('.system-message');
                chatHistory.innerHTML = '';
                if (systemMessage) chatHistory.appendChild(systemMessage);
                
                appendMessage('bot', 'Conversation history has been cleared.');
            } catch (error) {
                console.error('Failed to clear history:', error);
            }
        }
    });

    function appendMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        if (content instanceof DocumentFragment || content instanceof HTMLElement) {
            bubble.appendChild(content);
        } else {
            // Treat as text/html depending on needs. Safest is text, but we might want line breaks.
            // Using innerHTML here for simple formatting if needed, but be careful with XSS in real apps.
            // Since this comes from our own backend/LLM, we trust it slightly more, but better to escape generic text.
            bubble.innerHTML = String(content).replace(/\n/g, '<br>');
        }

        messageDiv.appendChild(sender === 'user' ? bubble : avatar); // Swap order based on flex-direction
        messageDiv.appendChild(sender === 'user' ? avatar : bubble);

        chatHistory.appendChild(messageDiv);
    }

    function appendLoading() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = id;
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="bubble">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatHistory.appendChild(messageDiv);
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
