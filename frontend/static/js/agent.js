/**
 * AI-POWERED CUSTOMER SUPPORT AGENT - AGENT DASHBOARD & WORKSPACE
 * File: frontend/static/js/agent.js
 */

document.addEventListener("DOMContentLoaded", () => {
  Auth.requireAuth(["agent", "admin"]);
  
  if (window.location.pathname.includes("agent_dashboard")) {
    loadAgentDashboard();
  } else if (window.location.pathname.includes("agent_ticket_details")) {
    loadTicketWorkspace();
  }
});

async function loadAgentDashboard() {
  try {
    const res = await API.get("/agent/tickets");
    const tickets = res.tickets || [];

    // Update KPI counters
    const openCount = tickets.filter(t => t.status === "OPEN").length;
    const inProgCount = tickets.filter(t => t.status === "IN_PROGRESS").length;
    const resolvedCount = tickets.filter(t => t.status === "RESOLVED").length;

    if (document.getElementById("stat-agent-total")) document.getElementById("stat-agent-total").innerText = tickets.length;
    if (document.getElementById("stat-agent-open")) document.getElementById("stat-agent-open").innerText = openCount;
    if (document.getElementById("stat-agent-progress")) document.getElementById("stat-agent-progress").innerText = inProgCount;
    if (document.getElementById("stat-agent-resolved")) document.getElementById("stat-agent-resolved").innerText = resolvedCount;

    renderAgentTickets(tickets);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderAgentTickets(tickets) {
  const tbody = document.getElementById("agent-tickets-tbody");
  if (!tbody) return;

  if (tickets.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:#94a3b8;">No tickets currently assigned to you.</td></tr>`;
    return;
  }

  tbody.innerHTML = tickets.map(t => `
    <tr>
      <td style="font-weight:700; color:var(--primary);">${t.ticket_number}</td>
      <td style="font-weight:600;">${t.title}</td>
      <td>${t.customer_name || 'Customer'}</td>
      <td><span class="badge" style="background:#f1f5f9; color:#475569;">${t.category}</span></td>
      <td><span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span></td>
      <td><span class="badge badge-${t.status.toLowerCase()}">${t.status}</span></td>
      <td>
        <a href="/agent_ticket_details.html?id=${t.id}" class="btn btn-primary btn-sm">Resolve Ticket</a>
      </td>
    </tr>
  `).join("");
}

async function toggleAgentAvailability(checkbox) {
  try {
    await API.put("/agent/status", { is_available: checkbox.checked });
    showToast(`Status updated to ${checkbox.checked ? "Available" : "Busy"}`, "success");
  } catch (err) {
    showToast(err.message, "error");
    checkbox.checked = !checkbox.checked;
  }
}

let activeTicket = null;

async function loadTicketWorkspace() {
  const urlParams = new URLSearchParams(window.location.search);
  const ticketId = urlParams.get("id");
  if (!ticketId) {
    window.location.href = "/agent_dashboard.html";
    return;
  }

  try {
    const res = await API.get(`/tickets/${ticketId}`);
    activeTicket = res.ticket;
    renderWorkspaceData(activeTicket);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderWorkspaceData(t) {
  document.getElementById("ws-ticket-number").innerText = t.ticket_number;
  document.getElementById("ws-title").innerText = t.title;
  document.getElementById("ws-description").innerText = t.description;
  document.getElementById("ws-customer-name").innerText = t.customer_name;
  document.getElementById("ws-customer-email").innerText = t.customer_email;
  document.getElementById("ws-category").innerText = t.category;
  
  const statusSelect = document.getElementById("ws-status-select");
  if (statusSelect) statusSelect.value = t.status;

  const priBadge = document.getElementById("ws-priority-badge");
  priBadge.innerText = t.priority;
  priBadge.className = `badge badge-${t.priority.toLowerCase()}`;

  renderTimelineNotes(t.notes || []);
}

function renderTimelineNotes(notes) {
  const container = document.getElementById("ws-notes-timeline");
  if (!container) return;

  if (notes.length === 0) {
    container.innerHTML = `<div style="color:#94a3b8; font-size:0.875rem; padding:1rem 0;">No communications recorded yet.</div>`;
    return;
  }

  container.innerHTML = notes.map(n => `
    <div class="timeline-item ${n.is_internal ? 'timeline-internal' : ''}">
      <div class="timeline-header">
        <span class="timeline-author">${n.author_name} (${n.author_role.toUpperCase()}) ${n.is_internal ? '🔒 Internal Note' : '💬 Public Reply'}</span>
        <span class="timeline-time">${new Date(n.created_at).toLocaleString()}</span>
      </div>
      <div style="font-size:0.9rem; color:#334155; line-height:1.5;">${n.note}</div>
    </div>
  `).join("");
}

async function sendAgentPublicResponse() {
  const textInput = document.getElementById("ws-public-response-text");
  const message = textInput.value.trim();
  if (!message) {
    showToast("Please enter a response message.", "error");
    return;
  }

  try {
    await API.post(`/agent/tickets/${activeTicket.id}/respond`, {
      message: message,
      status: "IN_PROGRESS"
    });
    textInput.value = "";
    showToast("Response sent to customer successfully.", "success");
    loadTicketWorkspace();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function addAgentInternalNote() {
  const noteInput = document.getElementById("ws-internal-note-text");
  const note = noteInput.value.trim();
  if (!note) {
    showToast("Please enter an internal note.", "error");
    return;
  }

  try {
    await API.post(`/tickets/${activeTicket.id}/notes`, {
      note: note,
      is_internal: true
    });
    noteInput.value = "";
    showToast("Internal note recorded.", "success");
    loadTicketWorkspace();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function updateTicketStatusFromSelect() {
  const status = document.getElementById("ws-status-select").value;
  try {
    await API.put(`/tickets/${activeTicket.id}/status`, { status });
    showToast(`Ticket status updated to ${status}.`, "success");
    loadTicketWorkspace();
  } catch (err) {
    showToast(err.message, "error");
  }
}

function generateAIDraft() {
  const draftBox = document.getElementById("ws-public-response-text");
  draftBox.value = `Hello ${activeTicket.customer_name},\n\nThank you for reaching out to support regarding ${activeTicket.title}. I have reviewed your case details and verified our system records. We are actively processing the necessary adjustments and will keep you updated within the next hour.\n\nBest regards,\n${Auth.getUser().full_name}\nCustomer Support Team`;
  showToast("Generated AI-assisted customer draft.", "info");
}
