/**
 * AI-POWERED CUSTOMER SUPPORT AGENT - ADMINISTRATOR PORTAL
 * File: frontend/static/js/admin.js
 */

document.addEventListener("DOMContentLoaded", () => {
  Auth.requireAuth(["admin"]);

  if (window.location.pathname.includes("admin_dashboard")) {
    loadAdminAnalytics();
  } else if (window.location.pathname.includes("knowledge_base")) {
    loadKnowledgeBase();
  } else if (window.location.pathname.includes("faq_management")) {
    loadFAQs();
  }
});

/* ==========================================================================
   Admin Analytics & Dashboard
   ========================================================================== */
async function loadAdminAnalytics() {
  try {
    const res = await API.get("/admin/analytics");
    const m = res.metrics;

    document.getElementById("adm-customers").innerText = m.total_customers;
    document.getElementById("adm-agents").innerText = m.total_agents;
    document.getElementById("adm-convs").innerText = m.total_conversations;
    document.getElementById("adm-tickets").innerText = m.total_tickets;
    document.getElementById("adm-open").innerText = m.open_tickets;
    document.getElementById("adm-resolved").innerText = m.resolved_tickets;
    document.getElementById("adm-escalated").innerText = m.escalated_tickets;
    document.getElementById("adm-csat").innerText = `${m.customer_satisfaction_rating}%`;

    renderCharts(m);
    loadRecentFeedback();
    loadLiveConversations();
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderCharts(m) {
  // Ticket Status & Priority Chart
  const ctxStatus = document.getElementById("chart-ticket-status");
  if (ctxStatus && window.Chart) {
    new Chart(ctxStatus, {
      type: "doughnut",
      data: {
        labels: ["Open", "In Progress", "Escalated", "Resolved"],
        datasets: [{
          data: [m.open_tickets, m.in_progress_tickets, m.escalated_tickets, m.resolved_tickets],
          backgroundColor: ["#3b82f6", "#f59e0b", "#ef4444", "#10b981"]
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  // Sentiment Distribution Chart
  const ctxSentiment = document.getElementById("chart-sentiment");
  if (ctxSentiment && window.Chart) {
    const s = m.sentiments || {};
    new Chart(ctxSentiment, {
      type: "bar",
      data: {
        labels: ["Positive", "Neutral", "Negative", "Frustrated"],
        datasets: [{
          label: "Conversations by Sentiment",
          data: [s["POSITIVE"] || 0, s["NEUTRAL"] || 0, s["NEGATIVE"] || 0, s["FRUSTRATED"] || 0],
          backgroundColor: ["#10b981", "#64748b", "#f97316", "#ef4444"]
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
}

async function loadRecentFeedback() {
  const container = document.getElementById("admin-feedback-tbody");
  if (!container) return;

  try {
    const res = await API.get("/admin/feedback", { limit: 5 });
    const fbs = res.feedback || [];
    if (fbs.length === 0) {
      container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:1.5rem; color:#94a3b8;">No customer feedback submitted yet.</td></tr>`;
      return;
    }
    container.innerHTML = fbs.map(f => `
      <tr>
        <td style="font-weight:600;">${f.customer_name || 'Customer'}</td>
        <td style="color:#f59e0b; font-weight:700;">★ ${f.rating} / 5</td>
        <td>${f.comment || 'No comment provided.'}</td>
        <td style="color:#94a3b8; font-size:0.8rem;">${new Date(f.created_at).toLocaleDateString()}</td>
      </tr>
    `).join("");
  } catch (e) {
    console.warn("Feedback load error", e);
  }
}

async function loadLiveConversations() {
  const container = document.getElementById("admin-convs-tbody");
  if (!container) return;

  try {
    const res = await API.get("/admin/conversations", { limit: 6 });
    const convs = res.conversations || [];
    container.innerHTML = convs.map(c => `
      <tr>
        <td style="font-weight:600;">${c.title || 'Support Session'}</td>
        <td>${c.customer_name || 'Guest User'}</td>
        <td><span class="badge" style="background:#f1f5f9;">${c.language.toUpperCase()}</span></td>
        <td><span class="sentiment-tag sentiment-${c.sentiment.toLowerCase()}">${c.sentiment}</span></td>
        <td><span class="badge badge-${c.status.toLowerCase()}">${c.status}</span></td>
        <td>${c.message_count || 0} msgs</td>
      </tr>
    `).join("");
  } catch (e) {
    console.warn("Conv load error", e);
  }
}

/* ==========================================================================
   Knowledge Base Management (RAG)
   ========================================================================== */
async function loadKnowledgeBase() {
  const tbody = document.getElementById("kb-documents-tbody");
  if (!tbody) return;

  try {
    const res = await API.get("/knowledge/documents");
    const docs = res.documents || [];

    if (docs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:#94a3b8;">No documents uploaded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = docs.map(d => `
      <tr>
        <td style="font-weight:700; color:var(--navy-900);">📄 ${d.title}</td>
        <td style="font-size:0.85rem; color:#64748b;">${d.file_name}</td>
        <td>${(d.file_size / 1024).toFixed(1)} KB</td>
        <td><span class="badge" style="background:#eff6ff; color:#1d4ed8;">${d.chunk_count} Chunks</span></td>
        <td><span class="badge badge-resolved">${d.status}</span></td>
        <td>
          <div style="display:flex; gap:0.5rem;">
            <button onclick="viewChunksModal('${d.id}')" class="btn btn-secondary btn-sm">Inspect Chunks</button>
            <button onclick="reindexDoc('${d.id}')" class="btn btn-outline btn-sm">Re-Index</button>
            <button onclick="deleteDoc('${d.id}')" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function uploadPDFFile() {
  const fileInput = document.getElementById("kb-file-input");
  const titleInput = document.getElementById("kb-doc-title");
  const file = fileInput.files[0];

  if (!file) {
    showToast("Please choose a PDF file to upload.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", titleInput.value.trim() || file.name.replace(".pdf", ""));

  const progress = document.getElementById("upload-progress");
  if (progress) progress.style.display = "block";

  try {
    showToast("Extracting text and generating vector embeddings...", "info");
    const res = await API.post("/knowledge/upload", formData);
    showToast(res.message, "success");
    fileInput.value = "";
    titleInput.value = "";
    loadKnowledgeBase();
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    if (progress) progress.style.display = "none";
  }
}

async function viewChunksModal(docId) {
  const modal = document.getElementById("chunks-modal");
  const container = document.getElementById("chunks-list");
  modal.classList.add("active");
  container.innerHTML = `<div style="text-align:center; padding:1.5rem;">Loading chunk embeddings...</div>`;

  try {
    const res = await API.get(`/knowledge/documents/${docId}/chunks`);
    const chunks = res.chunks || [];
    container.innerHTML = chunks.map(c => `
      <div style="padding:1rem; border:1px solid var(--border-light); border-radius:var(--radius-md); margin-bottom:0.75rem; background:#ffffff;">
        <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem; font-size:0.8rem; font-weight:700; color:var(--primary);">
          <span>Chunk #${c.chunk_index}</span>
          <span style="color:#64748b;">Page ${c.metadata.page || 1} • ${c.content.length} chars</span>
        </div>
        <div style="font-size:0.875rem; color:#334155; line-height:1.5;">${c.content}</div>
      </div>
    `).join("");
  } catch (err) {
    showToast(err.message, "error");
  }
}

function closeChunksModal() {
  document.getElementById("chunks-modal").classList.remove("active");
}

async function reindexDoc(docId) {
  try {
    showToast("Re-indexing chunks and vector embeddings...", "info");
    const res = await API.post(`/knowledge/documents/${docId}/reindex`, {});
    showToast(res.message, "success");
    loadKnowledgeBase();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteDoc(docId) {
  if (!confirm("Are you sure you want to permanently delete this document and all its vector embeddings?")) return;
  try {
    await API.delete(`/knowledge/documents/${docId}`);
    showToast("Document deleted successfully.", "success");
    loadKnowledgeBase();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function testRAGSearch() {
  const query = document.getElementById("test-rag-query").value.trim();
  const resultsBox = document.getElementById("rag-search-results");
  if (!query) return;

  resultsBox.innerHTML = `<div style="padding:1rem; color:#64748b;">Searching vector space...</div>`;

  try {
    const res = await API.post("/knowledge/search", { query, count: 3 });
    if (res.results.length === 0) {
      resultsBox.innerHTML = `<div style="padding:1rem; color:#94a3b8;">No chunks met similarity threshold.</div>`;
      return;
    }
    resultsBox.innerHTML = res.results.map((r, i) => `
      <div style="padding:0.75rem 1rem; border:1px solid var(--border-light); border-radius:var(--radius-md); margin-bottom:0.5rem; background:#ffffff;">
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; color:var(--primary); margin-bottom:0.25rem;">
          <span>Match #${i+1}: ${r.doc_title}</span>
          <span class="badge badge-resolved">${(r.similarity * 100).toFixed(1)}% Match</span>
        </div>
        <div style="font-size:0.85rem; color:#475569;">${r.content}</div>
      </div>
    `).join("");
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* ==========================================================================
   FAQ Management
   ========================================================================== */
async function loadFAQs() {
  const tbody = document.getElementById("faqs-tbody");
  if (!tbody) return;

  try {
    const res = await API.get("/faqs", { all: "true" });
    const faqs = res.faqs || [];

    tbody.innerHTML = faqs.map(f => `
      <tr>
        <td style="font-weight:600; color:var(--navy-900);">${f.question}</td>
        <td style="font-size:0.875rem; color:#475569; max-width:400px;">${f.answer}</td>
        <td><span class="badge" style="background:#f1f5f9;">${f.category}</span></td>
        <td><span class="badge ${f.is_active ? 'badge-resolved' : 'badge-closed'}">${f.is_active ? 'Active' : 'Inactive'}</span></td>
        <td>
          <button onclick="deleteFAQ('${f.id}')" class="btn btn-danger btn-sm">Delete</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function submitCreateFAQ() {
  const question = document.getElementById("faq-question").value.trim();
  const category = document.getElementById("faq-category").value;
  const answer = document.getElementById("faq-answer").value.trim();

  if (!question || !answer) {
    showToast("Please provide both question and answer.", "error");
    return;
  }

  try {
    await API.post("/faqs", { question, category, answer });
    showToast("FAQ created successfully.", "success");
    document.getElementById("faq-question").value = "";
    document.getElementById("faq-answer").value = "";
    loadFAQs();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function deleteFAQ(id) {
  if (!confirm("Are you sure you want to delete this FAQ?")) return;
  try {
    await API.delete(`/faqs/${id}`);
    showToast("FAQ deleted.", "success");
    loadFAQs();
  } catch (err) {
    showToast(err.message, "error");
  }
}
