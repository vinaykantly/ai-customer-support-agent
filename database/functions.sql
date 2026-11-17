-- ============================================================================
-- AI-POWERED CUSTOMER SUPPORT AGENT
-- Database Functions, Triggers & Vector Search
-- File: database/functions.sql
-- ============================================================================

-- 1. Semantic Similarity Search Function for RAG (pgvector Cosine Distance)
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(768),
    match_threshold FLOAT DEFAULT 0.65,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 2. Automatic Ticket Number Generator (Format: TIK-YYYYMMDD-XXXX)
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
DECLARE
    date_part TEXT;
    random_part TEXT;
    new_ticket_num TEXT;
    ticket_exists BOOLEAN;
BEGIN
    IF NEW.ticket_number IS NULL OR NEW.ticket_number = '' THEN
        date_part := TO_CHAR(CURRENT_DATE, 'YYYYMMDD');
        LOOP
            -- Generate a 4-character random uppercase alphanumeric string
            random_part := UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 4));
            new_ticket_num := 'TIK-' || date_part || '-' || random_part;
            
            -- Check for collision
            SELECT EXISTS(SELECT 1 FROM tickets WHERE ticket_number = new_ticket_num) INTO ticket_exists;
            IF NOT ticket_exists THEN
                NEW.ticket_number := new_ticket_num;
                EXIT;
            END IF;
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_generate_ticket_number
BEFORE INSERT ON tickets
FOR EACH ROW
EXECUTE FUNCTION generate_ticket_number();

-- 3. Automatic updated_at Timestamp Trigger
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_profiles_updated_at
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_conversations_updated_at
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_tickets_updated_at
BEFORE UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_knowledge_documents_updated_at
BEFORE UPDATE ON knowledge_documents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_faqs_updated_at
BEFORE UPDATE ON faqs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- 4. Sync Agent Current Ticket Count Trigger
CREATE OR REPLACE FUNCTION sync_agent_ticket_count()
RETURNS TRIGGER AS $$
BEGIN
    -- Update previous assigned agent if re-assigned or un-assigned
    IF TG_OP = 'UPDATE' AND OLD.assigned_agent_id IS NOT NULL AND OLD.assigned_agent_id <> NEW.assigned_agent_id THEN
        UPDATE agents 
        SET current_tickets_count = (
            SELECT COUNT(*) FROM tickets 
            WHERE assigned_agent_id = OLD.assigned_agent_id AND status IN ('OPEN', 'IN_PROGRESS', 'ESCALATED')
        )
        WHERE id = OLD.assigned_agent_id;
    END IF;

    -- Update newly assigned agent
    IF NEW.assigned_agent_id IS NOT NULL THEN
        UPDATE agents 
        SET current_tickets_count = (
            SELECT COUNT(*) FROM tickets 
            WHERE assigned_agent_id = NEW.assigned_agent_id AND status IN ('OPEN', 'IN_PROGRESS', 'ESCALATED')
        )
        WHERE id = NEW.assigned_agent_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_sync_agent_tickets
AFTER INSERT OR UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION sync_agent_ticket_count();
