# Database Entity-Relationship Diagram (ERD) & Data Dictionary

This document provides the complete database model, entity relationships, and table schema definitions for the **AI-Powered Customer Support Agent** platform.

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    PROFILES ||--o| AGENTS : "extends metadata"
    PROFILES ||--o{ CONVERSATIONS : "initiates"
    CONVERSATIONS ||--o{ MESSAGES : "contains"
    PROFILES ||--o{ TICKETS : "creates"
    PROFILES ||--o{ TICKETS : "assigned to"
    CONVERSATIONS ||--o| TICKETS : "escalates into"
    TICKETS ||--o{ TICKET_NOTES : "has"
    TICKETS ||--o{ TICKET_ASSIGNMENTS : "tracks"
    PROFILES ||--o{ KNOWLEDGE_DOCUMENTS : "uploads"
    KNOWLEDGE_DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "chunked into"
    PROFILES ||--o{ FEEDBACK : "submits"
    CONVERSATIONS ||--o| FEEDBACK : "rated on"
    PROFILES ||--o{ NOTIFICATIONS : "receives"

    PROFILES {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        string role
        string phone
        string avatar_url
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    AGENTS {
        uuid id PK,FK
        string department
        boolean is_available
        int max_tickets
        int current_tickets_count
        string_array skills
        timestamp created_at
    }

    CONVERSATIONS {
        uuid id PK
        uuid customer_id FK
        string session_id UK
        string title
        string language
        string sentiment
        string status
        timestamp created_at
        timestamp updated_at
    }

    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        string sender_type
        text content
        string intent
        string sentiment
        jsonb sources
        string language
        timestamp created_at
    }

    TICKETS {
        uuid id PK
        string ticket_number UK
        uuid customer_id FK
        uuid conversation_id FK
        string title
        text description
        string category
        string priority
        string status
        uuid assigned_agent_id FK
        timestamp created_at
        timestamp updated_at
        timestamp resolved_at
    }

    TICKET_NOTES {
        uuid id PK
        uuid ticket_id FK
        uuid author_id FK
        text note
        boolean is_internal
        timestamp created_at
    }

    TICKET_ASSIGNMENTS {
        uuid id PK
        uuid ticket_id FK
        uuid agent_id FK
        uuid assigned_by FK
        timestamp assigned_at
        string status
    }

    KNOWLEDGE_DOCUMENTS {
        uuid id PK
        string title
        string file_name
        string file_path
        int file_size
        string mime_type
        int chunk_count
        string status
        uuid uploaded_by FK
        timestamp created_at
        timestamp updated_at
    }

    DOCUMENT_CHUNKS {
        uuid id PK
        uuid document_id FK
        int chunk_index
        text content
        jsonb metadata
        vector_768 embedding
        timestamp created_at
    }

    FAQS {
        uuid id PK
        text question
        text answer
        string category
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    FEEDBACK {
        uuid id PK
        uuid conversation_id FK
        uuid ticket_id FK
        uuid customer_id FK
        int rating
        text comment
        timestamp created_at
    }

    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        string title
        string message
        string type
        string link
        boolean is_read
        timestamp created_at
    }
```

---

## 2. Table Data Dictionary

### `profiles`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, Default `uuid_generate_v4()` | Unique user identifier |
| `email` | `VARCHAR(255)` | UNIQUE, NOT NULL | Account email address |
| `password_hash` | `VARCHAR(255)` | NOT NULL | Werkzeug scrypt/pbkdf2 hash |
| `full_name` | `VARCHAR(150)` | NOT NULL | User's legal name |
| `role` | `VARCHAR(20)` | `CHECK ('customer', 'agent', 'admin')` | Access control role |
| `phone` | `VARCHAR(30)` | NULL | Optional telephone contact |
| `avatar_url` | `VARCHAR(500)` | NULL | Profile image URI |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | Account activity status |
| `created_at` | `TIMESTAMP` | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |
| `updated_at` | `TIMESTAMP` | DEFAULT CURRENT_TIMESTAMP | Last profile modification |

### `tickets`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Unique internal ticket UUID |
| `ticket_number` | `VARCHAR(30)` | UNIQUE, NOT NULL | Human-readable identifier (`TIK-YYYYMMDD-XXXX`) |
| `customer_id` | `UUID` | FK -> `profiles(id)` | Customer who opened the ticket |
| `conversation_id`| `UUID` | FK -> `conversations(id)`, NULL | Linked chat transcript if escalated |
| `title` | `VARCHAR(250)` | NOT NULL | Issue summary |
| `description` | `TEXT` | NOT NULL | Detailed problem statement |
| `category` | `VARCHAR(50)` | `CHECK ('BILLING', 'TECHNICAL', ...)` | Departmental category |
| `priority` | `VARCHAR(20)` | `CHECK ('LOW', 'MEDIUM', 'HIGH', 'URGENT')` | Urgency classification |
| `status` | `VARCHAR(20)` | `CHECK ('OPEN', 'IN_PROGRESS', ...)` | Ticket lifecycle state |
| `assigned_agent_id`| `UUID` | FK -> `profiles(id)`, NULL | Current handling agent |
| `resolved_at` | `TIMESTAMP` | NULL | Resolution completion timestamp |

### `document_chunks`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Unique chunk ID |
| `document_id` | `UUID` | FK -> `knowledge_documents(id)` | Parent PDF document |
| `chunk_index` | `INTEGER` | NOT NULL | Sequential chunk order in PDF |
| `content` | `TEXT` | NOT NULL | Extracted passage text |
| `metadata` | `JSONB` | DEFAULT `{}` | Page number, section, title |
| `embedding` | `vector(768)` | pgvector cosine indexing (HNSW) | 768-dim Gemini vector |
