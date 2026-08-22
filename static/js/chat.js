/**
 * Customer Support AI — Chat Client
 * Handles message send/receive, typing indicators, quick replies, and history.
 */

(function () {
  'use strict';

  // ── DOM Elements ──
  const messagesContainer = document.getElementById('messages');
  const messageInput = document.getElementById('message-input');
  const sendBtn = document.getElementById('send-btn');
  const typingIndicator = document.getElementById('typing-indicator');
  const quickRepliesContainer = document.getElementById('quick-replies');

  // ── State ──
  let isWaiting = false;

  // ── Initialize ──
  function init() {
    loadHistory();
    loadSuggestions();
    messageInput.focus();

    sendBtn.addEventListener('click', handleSend);
    messageInput.addEventListener('keydown', handleKeyDown);
    messageInput.addEventListener('input', autoResize);

    // Clear chat button
    const clearBtn = document.getElementById('clear-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', clearChat);
    }
  }

  // ── Send Message ──
  async function handleSend() {
    const text = messageInput.value.trim();
    if (!text || isWaiting) return;

    // Add user message
    appendMessage('user', text);
    messageInput.value = '';
    messageInput.style.height = '46px';
    isWaiting = true;
    sendBtn.disabled = true;

    // Hide quick replies after first message
    quickRepliesContainer.style.display = 'none';

    // Show typing indicator
    showTyping();

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text }),
      });

      const data = await response.json();
      hideTyping();

      if (response.ok) {
        appendMessage('bot', data.response, {
          type: data.type,
          category: data.category,
          confidence: data.confidence,
        });
      } else {
        appendMessage('bot', data.error || 'Something went wrong. Please try again.', {
          type: 'escalation',
        });
      }
    } catch (err) {
      hideTyping();
      appendMessage('bot', 'Unable to reach the server. Please check your connection and try again.', {
        type: 'escalation',
      });
    }

    isWaiting = false;
    sendBtn.disabled = false;
    messageInput.focus();
  }

  // ── Keyboard Handling ──
  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  // ── Auto-resize Textarea ──
  function autoResize() {
    this.style.height = '46px';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
  }

  // ── Append Message to Chat ──
  function appendMessage(role, content, meta = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    let badgeHTML = '';
    if (role === 'bot' && meta.type) {
      const badgeClass = `badge-${meta.type}`;
      const badgeLabel = meta.type === 'faq' ? 'FAQ' : meta.type === 'ai' ? 'AI' : 'Support';
      badgeHTML = `<span class="message-badge ${badgeClass}">${badgeLabel}</span>`;
    }

    let categoryHTML = '';
    if (role === 'bot' && meta.category && meta.category !== 'General') {
      categoryHTML = `<span class="category-tag">📁 ${meta.category}</span>`;
    }

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
      ${categoryHTML}
      <div class="bubble">${escapeHtml(content)}</div>
      <div class="message-meta">
        <span class="message-time">${timeStr}</span>
        ${badgeHTML}
      </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
  }

  // ── Typing Indicator ──
  function showTyping() {
    typingIndicator.classList.add('visible');
    scrollToBottom();
  }

  function hideTyping() {
    typingIndicator.classList.remove('visible');
  }

  // ── Quick Replies ──
  function loadSuggestions() {
    fetch('/suggestions')
      .then((res) => res.json())
      .then((data) => {
        if (data.suggestions && data.suggestions.length > 0) {
          quickRepliesContainer.innerHTML = '';
          data.suggestions.forEach((text) => {
            const btn = document.createElement('button');
            btn.className = 'quick-reply-btn';
            btn.textContent = text;
            btn.addEventListener('click', () => {
              messageInput.value = text;
              handleSend();
            });
            quickRepliesContainer.appendChild(btn);
          });
        }
      })
      .catch(() => {});
  }

  // ── Chat History ──
  function loadHistory() {
    fetch('/history')
      .then((res) => res.json())
      .then((data) => {
        if (data.history && data.history.length > 0) {
          // Hide welcome section if there's history
          const welcome = document.querySelector('.welcome-section');
          if (welcome) welcome.style.display = 'none';

          data.history.forEach((msg) => {
            appendMessage(msg.role, msg.content, msg.metadata || {});
          });
        }
      })
      .catch(() => {});
  }

  // ── Clear Chat ──
  async function clearChat() {
    try {
      await fetch('/clear', { method: 'POST' });
      // Remove all messages but keep welcome
      const messages = messagesContainer.querySelectorAll('.message');
      messages.forEach((m) => m.remove());
      const welcome = document.querySelector('.welcome-section');
      if (welcome) welcome.style.display = '';
      quickRepliesContainer.style.display = 'flex';
      loadSuggestions();
    } catch (err) {
      // Silently fail
    }
  }

  // ── Scroll to Bottom ──
  function scrollToBottom() {
    requestAnimationFrame(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
  }

  // ── Escape HTML ──
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ── Boot ──
  document.addEventListener('DOMContentLoaded', init);
})();
