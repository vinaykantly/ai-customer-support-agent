/**
 * AI-POWERED CUSTOMER SUPPORT AGENT - CHATBOT INTERACTION
 * File: frontend/static/js/chat.js
 */

let currentSessionId = localStorage.getItem("active_chat_session") || `sess_${Math.random().toString(36).substring(2, 12)}`;
localStorage.setItem("active_chat_session", currentSessionId);
let currentLanguage = "en";
let currentConversationId = null;

document.addEventListener("DOMContentLoaded", () => {
  setupChat();
  loadSuggestedQuestions();
  loadRecentSessions();
});

function setupChat() {
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const langSelect = document.getElementById("lang-select");

  if (langSelect) {
    langSelect.addEventListener("change", (e) => {
      currentLanguage = e.target.value;
      loadSuggestedQuestions();
      showToast(`Language switched to ${e.target.options[e.target.selectedIndex].text}`, "info");
    });
  }

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => handleSendMessage());
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handleSendMessage();
    });
  }
}

async function loadSuggestedQuestions() {
  const container = document.getElementById("suggested-questions-bar");
  if (!container) return;

  try {
    const res = await API.get("/chat/suggested-questions", { language: currentLanguage });
    container.innerHTML = "";
    (res.questions || []).forEach(q => {
      const chip = document.createElement("button");
      chip.className = "suggested-chip";
      chip.innerText = q;
      chip.onclick = () => {
        document.getElementById("chat-input").value = q;
        handleSendMessage();
      };
      container.appendChild(chip);
    });
  } catch (err) {
    console.warn("Could not load suggested questions", err);
  }
}

async function handleSendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  appendMessage({
    sender_type: "user",
    content: message,
    created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });

  showTypingIndicator();

  const user = Auth.getUser();
  try {
    const res = await API.post("/chat/message", {
      message: message,
      session_id: currentSessionId,
      language: currentLanguage,
      customer_id: user ? user.id : null
    });

    hideTypingIndicator();

    if (res.conversation_id) {
      currentConversationId = res.conversation_id;
    }

    appendMessage(res.message, res.suggest_escalation, res.sentiment);

    if (res.suggest_escalation) {
      document.getElementById("escalate-banner").style.display = "flex";
    }

  } catch (err) {
    hideTypingIndicator();
    appendMessage({
      sender_type: "bot",
      content: "Sorry, I encountered an issue connecting to the AI service. Please try again or create a support ticket.",
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    showToast(err.message, "error");
  }
}

function appendMessage(msg, showEscalateBtn = false, sentiment = "NEUTRAL") {
  const container = document.getElementById("messages-container");
  if (!container) return;

  const row = document.createElement("div");
  row.className = `message-row message-${msg.sender_type}`;

  const isUser = msg.sender_type === "user";
  const avatarHtml = isUser 
    ? "" 
    : `<div class="bot-avatar" style="width:34px; height:34px; font-size:0.95rem; flex-shrink:0;">🤖</div>`;

  let sourcesHtml = "";
  if (msg.sources && msg.sources.length > 0) {
    sourcesHtml = `
      <div class="sources-container">
        <span class="sources-label">📚 Verified Official Sources:</span>
        <div style="display:flex; flex-wrap:wrap; gap:0.35rem;">
          ${msg.sources.map(s => `
            <span class="source-chip" title="${s.section || ''}">
              📄 ${s.title}
            </span>
          `).join("")}
        </div>
      </div>
    `;
  }

  let escalateHtml = "";
  if (showEscalateBtn && !isUser) {
    escalateHtml = `
      <div style="margin-top:0.75rem;">
        <button onclick="triggerEscalation()" class="btn btn-danger btn-sm">
          🚨 Connect with Human Support Agent
        </button>
      </div>
    `;
  }

  row.innerHTML = `
    ${avatarHtml}
    <div class="bubble">
      <div>${formatMessageContent(msg.content)}</div>
      ${sourcesHtml}
      ${escalateHtml}
      <span class="msg-time">${msg.created_at || ""}</span>
    </div>
  `;

  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

function formatMessageContent(text) {
  if (!text) return "";
  // Simple markdown conversion: bold, lists, and line breaks
  let formatted = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n\n/g, "<br/><br/>")
    .replace(/\n/g, "<br/>");
  return formatted;
}

function showTypingIndicator() {
  const container = document.getElementById("messages-container");
  let ind = document.getElementById("typing-indicator-row");
  if (!ind) {
    ind = document.createElement("div");
    ind.id = "typing-indicator-row";
    ind.className = "message-row message-bot";
    ind.innerHTML = `
      <div class="bot-avatar" style="width:34px; height:34px; font-size:0.95rem;">🤖</div>
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    container.appendChild(ind);
  }
  container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
  const ind = document.getElementById("typing-indicator-row");
  if (ind) ind.remove();
}

async function triggerEscalation() {
  const user = Auth.getUser();
  try {
    showToast("Escalating to human agent queue...", "info");
    const res = await API.post("/chat/escalate", {
      conversation_id: currentConversationId,
      customer_id: user ? user.id : null,
      title: "Customer Escalation via AI Assistant",
      priority: "HIGH"
    });

    showToast(`Support Ticket ${res.ticket.ticket_number} created successfully!`, "success");
    setTimeout(() => {
      window.location.href = "/customer_tickets.html";
    }, 1200);
  } catch (err) {
    showToast(`Escalation failed: ${err.message}`, "error");
  }
}

async function loadRecentSessions() {
  const user = Auth.getUser();
  if (!user) return;

  const list = document.getElementById("sessions-list");
  if (!list) return;

  try {
    const res = await API.get("/chat/conversations");
    list.innerHTML = "";
    (res.conversations || []).forEach(c => {
      const item = document.createElement("div");
      item.className = `session-item ${c.session_id === currentSessionId ? 'active' : ''}`;
      item.innerHTML = `
        <div class="session-title">${c.title || 'Support Session'}</div>
        <div class="session-meta">
          <span>${c.status}</span>
          <span>${new Date(c.updated_at).toLocaleDateString()}</span>
        </div>
      `;
      item.onclick = () => loadSession(c.id, c.session_id);
      list.appendChild(item);
    });
  } catch (err) {
    console.warn("Could not load sessions", err);
  }
}

async function loadSession(convId, sessId) {
  currentConversationId = convId;
  currentSessionId = sessId;
  localStorage.setItem("active_chat_session", sessId);

  const container = document.getElementById("messages-container");
  container.innerHTML = "";

  try {
    const res = await API.get(`/chat/conversations/${convId}`);
    (res.messages || []).forEach(m => appendMessage(m));
    loadRecentSessions();
  } catch (err) {
    showToast(err.message, "error");
  }
}

function openFeedbackModal() {
  const modal = document.getElementById("feedback-modal");
  if (modal) modal.classList.add("active");
}

function closeFeedbackModal() {
  const modal = document.getElementById("feedback-modal");
  if (modal) modal.classList.remove("active");
}

let selectedRating = 5;
function setStarRating(num) {
  selectedRating = num;
  document.querySelectorAll(".star-rating .star").forEach((el, idx) => {
    el.classList.toggle("active", idx < num);
  });
}

async function submitChatFeedback() {
  const comment = document.getElementById("feedback-comment").value;
  const user = Auth.getUser();
  try {
    await API.post("/chat/feedback", {
      rating: selectedRating,
      comment: comment,
      conversation_id: currentConversationId,
      customer_id: user ? user.id : null
    });
    showToast("Feedback submitted. Thank you!", "success");
    closeFeedbackModal();
  } catch (err) {
    showToast(err.message, "error");
  }
}
