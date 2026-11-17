/**
 * AI-POWERED CUSTOMER SUPPORT AGENT - MAIN APP SCRIPT
 * File: frontend/static/js/main.js
 */

document.addEventListener("DOMContentLoaded", () => {
  setupNavbar();
  highlightActiveNav();
  setupNotifications();
});

function setupNavbar() {
  const user = Auth.getUser();
  const navContainer = document.getElementById("nav-user-slot");
  if (!navContainer) return;

  if (user) {
    const initials = user.full_name
      ? user.full_name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase()
      : "U";

    navContainer.innerHTML = `
      <div style="display:flex; align-items:center; gap:1rem;">
        <div style="position:relative; cursor:pointer;" id="notif-bell-btn">
          <span style="font-size:1.25rem;">🔔</span>
          <span id="notif-count-badge" class="badge badge-urgent" style="position:absolute; top:-6px; right:-8px; font-size:0.65rem; padding:0.15rem 0.35rem; display:none;">0</span>
        </div>
        <a href="/profile.html" style="display:flex; align-items:center; gap:0.6rem; text-decoration:none;">
          <div class="user-avatar">${initials}</div>
          <div style="display:flex; flex-direction:column;">
            <span style="font-weight:600; font-size:0.875rem; color:#ffffff;">${user.full_name}</span>
            <span style="font-size:0.7rem; color:#94a3b8; text-transform:uppercase;">${user.role}</span>
          </div>
        </a>
        <button onclick="Auth.logout()" class="btn btn-secondary btn-sm" style="border-radius:4px; padding:0.35rem 0.65rem;">Logout</button>
      </div>
    `;
  } else {
    navContainer.innerHTML = `
      <div style="display:flex; align-items:center; gap:0.75rem;">
        <a href="/login.html" class="btn btn-secondary btn-sm">Log In</a>
        <a href="/register.html" class="btn btn-primary btn-sm">Sign Up</a>
      </div>
    `;
  }
}

function highlightActiveNav() {
  const currentPath = window.location.pathname;
  document.querySelectorAll(".sidebar-link, .nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href && (currentPath.endsWith(href) || (currentPath === "/" && href.includes("index")))) {
      link.classList.add("active");
    }
  });
}

async function setupNotifications() {
  const user = Auth.getUser();
  if (!user) return;

  try {
    const res = await API.get("/notifications", { unread: "true" });
    const countBadge = document.getElementById("notif-count-badge");
    if (countBadge && res.notifications && res.notifications.length > 0) {
      countBadge.innerText = res.notifications.length;
      countBadge.style.display = "inline-flex";
    }
  } catch (e) {
    // Silently ignore notification fetch errors
  }
}
