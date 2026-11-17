# REST API Documentation: AI-Powered Customer Support Agent

Base URL: `http://localhost:5000/api`

---

## 1. Authentication Endpoints (`/api/auth`)

### `POST /api/auth/register`
Creates a new customer or support agent profile.

**Request Body:**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "Password@123",
  "role": "customer",
  "phone": "+1-800-555-0199",
  "department": "General Support"
}
```

**Response (201 Created):**
```json
{
  "message": "Registration successful.",
  "access_token": "eyJhbGciOi...",
  "user": {
    "id": "c0000000-0000-0000-0000-000000000001",
    "email": "jane@example.com",
    "full_name": "Jane Doe",
    "role": "customer"
  }
}
```

---

### `POST /api/auth/login`
Authenticates a user and issues a signed JWT bearer token.

**Request Body:**
```json
{
  "email": "admin@company.com",
  "password": "Admin@123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful.",
  "access_token": "eyJhbGciOi...",
  "user": {
    "id": "a0000000-0000-0000-0000-000000000001",
    "email": "admin@company.com",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```

---

## 2. AI Chat & RAG Endpoints (`/api/chat`)

### `POST /api/chat/message`
Submits a customer message for RAG retrieval and Gemini generation.

**Request Body:**
```json
{
  "message": "What is your refund policy for annual subscriptions?",
  "session_id": "sess_demo_101",
  "language": "en"
}
```

**Response (200 OK):**
```json
{
  "session_id": "sess_demo_101",
  "conversation_id": "c1000000-0000-0000-0000-000000000001",
  "sentiment": "NEUTRAL",
  "intent": "BILLING_INQUIRY",
  "suggest_escalation": false,
  "message": {
    "sender_type": "bot",
    "content": "According to our Official Company Support Policy, customers may request a full refund within 30 calendar days...",
    "sources": [
      {
        "title": "Official Company Support Policy & SLA Manual",
        "section": "2.3",
        "similarity": 0.8842
      }
    ],
    "language": "en"
  }
}
```

---

### `POST /api/chat/escalate`
Converts a conversational chat session into a formal support ticket.

**Request Body:**
```json
{
  "conversation_id": "c1000000-0000-0000-0000-000000000001",
  "title": "Customer Escalation via AI Assistant",
  "category": "BILLING",
  "priority": "HIGH"
}
```

**Response (201 Created):**
```json
{
  "message": "Successfully escalated to ticket TIK-20261115-A101.",
  "ticket": {
    "ticket_number": "TIK-20261115-A101",
    "title": "Customer Escalation via AI Assistant",
    "status": "OPEN",
    "priority": "HIGH"
  }
}
```

---

## 3. Support Tickets Endpoints (`/api/tickets`)

### `POST /api/tickets`
Creates a support ticket manually. *Requires Bearer Token.*

**Request Body:**
```json
{
  "title": "SAML SSO Certificate Expiring",
  "category": "TECHNICAL",
  "priority": "URGENT",
  "description": "Our Okta certificate will expire in 3 days. Need assistance rotating keys."
}
```

### `GET /api/tickets`
Retrieves tickets filtered by role:
- Customers see their own tickets.
- Agents see tickets assigned to them.
- Admins see all tickets with status/priority filtering (`?status=OPEN&priority=HIGH`).

### `PUT /api/tickets/<id>/status`
Updates ticket lifecycle state. *Requires Agent or Admin role.*
- Allowed statuses: `OPEN`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`, `CLOSED`.

### `POST /api/tickets/<id>/notes`
Adds communication note.
- Customers can only add public notes (`is_internal: false`).
- Agents and Admins can add both public notes and private internal notes (`is_internal: true`).

---

## 4. Support Agent Endpoints (`/api/agent`)

### `GET /api/agent/tickets`
Returns assigned tickets sorted by urgency.

### `POST /api/agent/tickets/<id>/respond`
Submits public response to the customer and transitions ticket to `IN_PROGRESS`.

### `PUT /api/agent/status`
Updates agent availability toggle, department, and max ticket capacity.

---

## 5. Administrator Endpoints (`/api/admin`)

### `GET /api/admin/analytics`
Returns executive dashboard KPIs:
- `total_customers`, `total_agents`, `total_conversations`, `total_tickets`
- `open_tickets`, `in_progress_tickets`, `resolved_tickets`, `escalated_tickets`
- `customer_satisfaction_rating` (CSAT %)
- `categories`, `priorities`, `sentiments`, `languages` distributions

---

## 6. Knowledge Base Endpoints (`/api/knowledge`)

### `POST /api/knowledge/upload`
Uploads and indexes PDF documents into pgvector embeddings. *Requires Admin.*
- Content-Type: `multipart/form-data`
- Form Fields: `file` (PDF), `title` (string)

### `POST /api/knowledge/search`
Live RAG Semantic Search test sandbox.
- Body: `{"query": "refund policy", "count": 3}`
