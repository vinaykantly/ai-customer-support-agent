# AI-Powered Customer Support Agent

An enterprise-grade, production-style intelligent customer support web application combining **Generative AI (Google Gemini)**, **Retrieval-Augmented Generation (RAG) with vector embeddings (Supabase pgvector)**, multi-tier **Role-Based Access Control (Customer, Agent, Admin)**, and an **automated ticket escalation lifecycle**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-REST%20API-lightgrey?logo=flask)
![Gemini](https://img.shields.io/badge/Google-Gemini%201.5%20Flash-orange?logo=google)
![Supabase](https://img.shields.io/badge/Supabase-pgvector-emerald?logo=supabase)
![Tests](https://img.shields.io/badge/Tests-30%2F30%20Passing-brightgreen?logo=pytest)

---

## 🌟 Executive Summary & Key Highlights

- **🧠 Google Gemini GenAI**: Context-aware natural language understanding with strict anti-hallucination guardrails. Never invents company policies or customer transaction data.
- **📚 pgvector RAG Pipeline**: Extracts and semantically chunks company PDF manuals, computes 768-dimensional embeddings, and grounds AI responses with clickable source document citations.
- **🌐 Trilingual Support**: Native conversational support in **English**, **Kannada (ಕನ್ನಡ)**, and **Hindi (हिन्दी)** with instant language toggling.
- **❤️ Sentiment & Frustration Detection**: Classifies customer emotion (`POSITIVE`, `NEUTRAL`, `NEGATIVE`, `FRUSTRATED`) and offers immediate 1-click human agent escalation when frustration or explicit requests are detected.
- **🎫 Automated Support Tickets**: Generates formatted ticket tracking IDs (`TIK-YYYYMMDD-XXXX`), balances workloads across available agents, and archives complete AI chat transcripts.
- **🎧 Agent Resolution Workbench**: Priority queues ranked by urgency SLA, AI-assisted response drafting, customer communication timeline, and private internal notes.
- **📊 Executive Admin Command**: Real-time KPI analytics, CSAT satisfaction ratings, interactive Chart.js volume trends, PDF knowledge base manager, and live vector search test sandbox.
- **⚡ Dual-Mode Database Engine**: Connects natively to **Supabase Cloud (PostgreSQL + pgvector + RLS)**, or runs instantly in **Zero-Config Local Evaluation Mode (Persistent SQLite + Vector Engine)** for immediate recruiter demonstration without requiring external keys!

---

## ⚡ 1-Click Evaluation Credentials (For Recruiters)

The application includes a built-in 1-Click login filler on `/login.html`:

| Role | Email | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@company.com` | `Admin@123` | Executive analytics, CSAT %, PDF RAG indexing, FAQ manager |
| **Support Agent** | `agent.rajesh@company.com` | `Agent@123` | Priority queue, AI draft generator, customer replies, private notes |
| **Customer** | `customer@example.com` | `Customer@123` | Trilingual AI chatbot, complaint submission, ticket tracking |

---

## 🚀 Quick Start (Running Locally)

### 1. Clone & Enter Directory
```bash
cd ai-customer-support
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Server
```bash
python run.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🧪 Automated Testing Suite (30/30 Tests Passing)

Execute the complete pytest test suite covering authentication, RAG extraction, prompt injection defense, RBAC boundaries, and ticket workflows:
```bash
python -m pytest tests/ -v
```

Output:
```
============================= 30 passed in 3.20s ==============================
```

---

## 📁 System Architecture & Directory Structure

```
ai-customer-support/
├── backend/
│   ├── app.py                     # Flask application factory & page routes
│   ├── config.py                  # Dual-mode configuration profiles
│   ├── middleware/
│   │   ├── auth_middleware.py     # JWT signing, decoding & RBAC decorators
│   │   ├── rate_limiter.py        # Sliding window rate limiter
│   │   └── security.py            # Prompt injection defense & sanitization
│   ├── routes/
│   │   ├── auth_routes.py         # Registration, login, profile endpoints
│   │   ├── chat_routes.py         # AI chatbot, suggested questions, escalation
│   │   ├── ticket_routes.py       # Ticket creation, status updates, notes
│   │   ├── agent_routes.py        # Agent queue, availability & responses
│   │   ├── admin_routes.py        # Analytics KPIs, conversation monitoring
│   │   ├── knowledge_routes.py    # PDF upload, chunking, pgvector search bench
│   │   ├── faq_routes.py          # FAQ CRUD
│   │   └── notification_routes.py # In-app notification alerts
│   ├── services/
│   │   ├── gemini_service.py      # Google Gemini 1.5 Flash API connector
│   │   ├── rag_service.py         # RAG retrieval & source grounding
│   │   ├── embedding_service.py   # text-embedding-004 generator
│   │   ├── pdf_service.py         # PDF parser & semantic text chunker
│   │   ├── sentiment_service.py   # Sentiment & intent classification
│   │   └── notification_service.py# Alert dispatcher
│   └── database/
│       ├── db_manager.py          # Unified database manager (Supabase + SQLite)
│       └── models.py              # Schemas & data helpers
├── database/
│   ├── schema.sql                 # PostgreSQL & Supabase schema with pgvector
│   ├── rls_policies.sql           # Row Level Security (RLS) policies
│   ├── functions.sql              # Vector similarity function & triggers
│   └── seed_data.sql              # Realistic seed data for all roles
├── frontend/
│   ├── templates/                 # 12 Responsive HTML5 Pages
│   │   ├── index.html             # Landing page
│   │   ├── register.html          # Registration & onboarding
│   │   ├── login.html             # Login with 1-click demo buttons
│   │   ├── customer_dashboard.html# Customer portal
│   │   ├── chat.html              # Trilingual AI Chatbot with source citations
│   │   ├── customer_tickets.html  # Ticket complaint tracker & modal
│   │   ├── agent_dashboard.html   # Support agent queue & status toggle
│   │   ├── agent_ticket_details.html # Agent resolution workbench & AI draft
│   │   ├── admin_dashboard.html   # Executive KPIs & Chart.js analytics
│   │   ├── knowledge_base.html    # PDF knowledge manager & vector sandbox
│   │   ├── faq_management.html    # FAQ repository editor
│   │   └── profile.html           # Profile & security settings
│   └── static/
│       ├── css/
│       │   ├── main.css           # Core Dark Navy & Blue SaaS design system
│       │   ├── chat.css           # Message bubbles, sources, typing animation
│       │   └── dashboard.css      # KPI widgets, tables, dropzones, workspace
│       └── js/
│           ├── api.js             # Fetch client with JWT & toast notifications
│           ├── auth.js            # Auth state, route guards & demo fillers
│           ├── chat.js            # Multilingual AI interaction & escalation
│           ├── tickets.js         # Ticket creation & response timeline
│           ├── agent.js           # Agent queue, AI drafting & status transitions
│           ├── admin.js           # Analytics charts, PDF upload & chunk modal
│           └── main.js            # App initialization & notifications
├── docs/                          # Detailed Technical Documentation
│   ├── SYSTEM_ARCHITECTURE.md     # Architecture diagrams & RAG pipeline
│   ├── DATABASE_ERD.md            # Entity-relationship diagram & data dictionary
│   ├── API_DOCUMENTATION.md       # Complete REST API reference
│   ├── DATABASE_SETUP.md          # Supabase pgvector & local setup guide
│   ├── ENVIRONMENT_CONFIG.md      # Environment variable specifications
│   ├── INSTALLATION.md            # Installation & virtualenv guide
│   ├── TESTING.md                 # Testing documentation & manual scenarios
│   └── DEPLOYMENT.md              # Docker & production cloud deployment
├── uploads/                       # Uploaded PDF document storage
├── tests/                         # Pytest test suite (30 tests)
├── .env.example                   # Environment configuration template
├── requirements.txt               # Python package dependencies
└── run.py                         # Application startup runner
```

---

## 🔒 Security & Guardrails

1. **Prompt Injection & Jailbreak Defense**: Filters incoming user messages against malicious jailbreak patterns (`ignore previous instructions`, `DAN mode`, `reveal system prompt`, etc.) before passing to the AI pipeline.
2. **Strict Document Grounding**: System instructions explicitly prohibit inventing policies, financial commitments, pricing plans, or bank confirmations. If the retrieved context is insufficient, the model offers human agent escalation.
3. **Row-Level Security (RLS)**: Enforces strict data isolation on Supabase PostgreSQL. Customers can only view their own tickets; agents can only view assigned cases; administrators have holistic oversight.
4. **Customer Privacy**: Internal notes written by agents are strictly hidden from customer view.
5. **Rate Limiting**: Sliding window rate limiter prevents resource exhaustion on chat generation and authentication endpoints.

---

## 📖 In-Depth Documentation Links

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Database ERD & Data Dictionary](docs/DATABASE_ERD.md)
- [REST API Reference](docs/API_DOCUMENTATION.md)
- [Database Setup & Supabase pgvector](docs/DATABASE_SETUP.md)
- [Environment Configuration Guide](docs/ENVIRONMENT_CONFIG.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Testing & Quality Assurance](docs/TESTING.md)
- [Production Deployment & Docker](docs/DEPLOYMENT.md)

---

## 📄 License & Portfolio Rights

Developed as a modern, production-grade AI engineering portfolio application. Free to use, adapt, and deploy.
#   a i - c u s t o m e r - s u p p o r t  
 