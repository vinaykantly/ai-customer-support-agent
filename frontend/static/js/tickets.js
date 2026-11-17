/**
 * AI-POWERED CUSTOMER SUPPORT AGENT - TICKETS MANAGEMENT
 * File: frontend/static/js/tickets.js
 */

document.addEventListener("DOMContentLoaded", () => {
  Auth.requireAuth(["customer", "agent", "admin"]);
  loadTickets();
  setupFilter();
});

let allTickets = [];

async function loadTickets() {
  const tbody = document.getElementById("tickets-tbody");
  if (!tbody) return;

  try {
    const res = await API.get("/tickets");
    allTickets = res.tickets || [];
    renderTicketsTable(allTickets);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function renderTicketsTable(tickets) {
  const tbody = document.getElementById("tickets-tbody");
  if (!tbody) return;

  if (tickets.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:#94a3b8;">No support tickets found.</td></tr>`;
    return;
  }

  tbody.innerHTML = tickets.map(t => `
    <tr>
      <td style="font-weight:700; color:var(--primary);">${t.ticket_number}</td>
      <td style="font-weight:600;">${t.title}</td>
      <td><span class="badge" style="background:#f1f5f9; color:#475569;">${t.category}</span></td>
      <td><span class="badge badge-${t.priority.toLowerCase()}">${t.priority}</span></td>
      <td><span class="badge badge-${t.status.toLowerCase()}">${t.status}</span></td>
      <td>
        <button onclick="viewTicketModal('${t.id}')" class="btn btn-secondary btn-sm">View Details</button>
      </td>
    </tr>
  `).join("");
}

function setupFilter() {
  const select = document.getElementById("status-filter");
  if (!select) return;

  select.addEventListener("change", (e) => {
    const val = e.target.value;
    if (!val || val === "ALL") {
      renderTicketsTable(allTickets);
    } else {
      renderTicketsTable(allTickets.filter(t => t.status === val));
    }
  });
}

function openCreateTicketModal() {
  document.getElementById("create-ticket-modal").classList.add("active");
}

function closeCreateTicketModal() {
  document.getElementById("create-ticket-modal").classList.remove("active");
}

async function submitCreateTicket() {
  const title = document.getElementById("ticket-title").value.trim();
  const category = document.getElementById("ticket-category").value;
  const priority = document.getElementById("ticket-priority").value;
  const description = document.getElementById("ticket-description").value.trim();

  if (!title || !description) {
    showToast("Please provide both title and description.", "error");
    return;
  }

  try {
    const res = await API.post("/tickets", {
      title,
      category,
      priority,
      description
    });

    showToast(`Ticket ${res.ticket.ticket_number} created successfully!`, "success");
    closeCreateTicketModal();
    document.getElementById("create-ticket-form").reset();
    loadTickets();
  } catch (err) {
    showToast(err.message, "error");
  }
}

let activeTicketId = null;

async function viewTicketModal(ticketId) {
  activeTicketId = ticketId;
  const modal = document.getElementById("ticket-details-modal");
  modal.classList.add("active");

  try {
    const res = await API.get(`/tickets/${ticketId}`);
    const t = res.ticket;

    document.getElementById("dt-ticket-num").innerText = t.ticket_number;
    document.getElementById("dt-title").innerText = t.title;
    document.getElementById("dt-desc").innerText = t.description;
    document.getElementById("dt-status").innerText = t.status;
    document.getElementById("dt-status").className = `badge badge-${t.status.toLowerCase()}`;
    document.getElementById("dt-priority").innerText = t.priority;
    document.getElementById("dt-priority").className = `badge badge-${t.priority.toLowerCase()}`;
    document.getElementById("dt-agent").innerText = t.agent_name || "Assigned to Queue";

    renderNotes(t.notes || []);
  } catch (err) {
    showToast(err.message, "error");
  }
}

function closeTicketDetailsModal() {
  document.getElementById("ticket-details-modal").classList.remove("active");
}

function renderNotes(notes) {
  const container = document.getElementById("ticket-notes-timeline");
  if (!container) return;

  if (notes.length === 0) {
    container.innerHTML = `<div style="color:#94a3b8; font-size:0.875rem; padding:1rem 0;">No responses yet from support team.</div>`;
    return;
  }

  container.innerHTML = notes.map(n => `
    <div class="timeline-item ${n.is_internal ? 'timeline-internal' : ''}">
      <div class="timeline-header">
        <span class="timeline-author">${n.author_name} (${n.author_role.toUpperCase()})</span>
        <span class="timeline-time">${new Date(n.created_at).toLocaleString()}</span>
      </div>
      <div style="font-size:0.9rem; color:#334155;">${n.note}</div>
    </div>
  `).join("");
}

async function submitTicketReply() {
  const replyInput = document.getElementById("ticket-reply-text");
  const note = replyInput.value.trim();
  if (!note) return;

  try {
    await API.post(`/tickets/${activeTicketId}/notes`, {
      note: note,
      is_internal: false
    });
    replyInput.value = "";
    showToast("Reply sent to support agent.", "success");
    viewTicketModal(activeTicketId);
  } catch (err) {
    showToast(err.message, "error");
  }
}
