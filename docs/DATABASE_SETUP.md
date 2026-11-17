# Database Setup & Configuration Guide

The **AI-Powered Customer Support Agent** features a dual-mode database engine:
1. **Production Mode (Supabase PostgreSQL + pgvector + RLS)**: Scalable cloud database with native vector similarity matching and row-level security.
2. **Zero-Config Evaluation Mode (Local SQLite + Vector Engine)**: Automatically enabled when Supabase credentials are not provided. Uses persistent local storage and cosine vector math so recruiters and automated CI pipelines can run the entire platform immediately out of the box!

---

## 1. Setting Up Supabase Cloud (Production)

### Step 1: Create a Supabase Project
1. Navigate to [Supabase.com](https://supabase.com/) and create a free project.
2. Note your **Project URL** and **API Keys** (`anon` public key and `service_role` key) from **Project Settings > API**.

### Step 2: Enable pgvector Extension
In your Supabase project dashboard, navigate to **SQL Editor** and run:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
```

### Step 3: Execute Database Scripts in Sequence
Copy and execute the contents of the following SQL files located in `database/`:

1. `database/schema.sql`:
   - Creates tables (`profiles`, `agents`, `conversations`, `messages`, `tickets`, `ticket_assignments`, `ticket_notes`, `knowledge_documents`, `document_chunks`, `faqs`, `feedback`, `notifications`).
   - Configures 768-dimensional vector column for Gemini embeddings.
   - Creates HNSW index on `document_chunks.embedding` using cosine distance ops.

2. `database/rls_policies.sql`:
   - Enables Row Level Security on all tables.
   - Enforces isolation between customers, agents, and administrators.

3. `database/functions.sql`:
   - Creates `match_document_chunks` for pgvector cosine similarity search.
   - Creates `generate_ticket_number` trigger (`TIK-YYYYMMDD-XXXX`).
   - Creates `set_updated_at` trigger.
   - Creates `sync_agent_ticket_count` trigger to maintain agent workloads.

4. `database/seed_data.sql`:
   - Seeds initial administrative accounts, support agents, customer profiles, verified FAQs, sample documents, and seed tickets.

---

## 2. Configuring Backend Environment

Add your Supabase credentials into your `.env` file:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DB_MODE=supabase
```

Restart the Flask server:
```bash
python run.py
```

---

## 3. Zero-Config Local Mode (Offline & Portfolios)

If you clone the project or run it without internet access or Supabase credentials:
- Leave `SUPABASE_URL` and `SUPABASE_KEY` empty in `.env`.
- The application automatically initializes SQLite storage at `backend/database/local_support.db`.
- Vector embeddings and cosine similarity searches are calculated locally.
- Seed data (Admin, Agents, Customer, FAQs, Knowledge chunks, Tickets) is populated automatically on first run.
