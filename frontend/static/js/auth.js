/**
 * AI-POWERED CUSTOMER SUPPORT AGENT - AUTHENTICATION UTILITY
 * File: frontend/static/js/auth.js
 */

const Auth = {
  getUser() {
    try {
      const data = localStorage.getItem("user_profile");
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  setUser(user) {
    if (user) {
      localStorage.setItem("user_profile", JSON.stringify(user));
    } else {
      localStorage.removeItem("user_profile");
    }
  },

  isAuthenticated() {
    return Boolean(API.getToken() && this.getUser());
  },

  async login(email, password) {
    const res = await API.post("/auth/login", { email, password });
    if (res.access_token && res.user) {
      API.setToken(res.access_token);
      this.setUser(res.user);
    }
    return res;
  },

  async register(data) {
    const res = await API.post("/auth/register", data);
    if (res.access_token && res.user) {
      API.setToken(res.access_token);
      this.setUser(res.user);
    }
    return res;
  },

  logout() {
    API.post("/auth/logout", {}).catch(() => {});
    API.setToken(null);
    this.setUser(null);
    window.location.href = "/login.html";
  },

  requireAuth(allowedRoles = []) {
    const user = this.getUser();
    if (!this.isAuthenticated() || !user) {
      window.location.href = "/login.html";
      return false;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
      showToast(`Unauthorized: Requires ${allowedRoles.join(" or ")} role`, "error");
      // Redirect to their respective dashboard
      if (user.role === "admin") window.location.href = "/admin_dashboard.html";
      else if (user.role === "agent") window.location.href = "/agent_dashboard.html";
      else window.location.href = "/customer_dashboard.html";
      return false;
    }

    return true;
  },

  fillDemo(role) {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    if (!emailInput || !passwordInput) return;

    if (role === "admin") {
      emailInput.value = "admin@company.com";
      passwordInput.value = "Admin@123";
    } else if (role === "agent") {
      emailInput.value = "agent.rajesh@company.com";
      passwordInput.value = "Agent@123";
    } else if (role === "customer") {
      emailInput.value = "customer@example.com";
      passwordInput.value = "Customer@123";
    }
    showToast(`Autofilled demo credentials for ${role.toUpperCase()}`, "info");
  }
};
