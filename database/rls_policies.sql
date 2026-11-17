-- ============================================================================
-- AI-POWERED CUSTOMER SUPPORT AGENT
-- Supabase Row Level Security (RLS) Policies
-- File: database/rls_policies.sql
-- ============================================================================

-- Enable Row Level Security on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE faqs ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Helper function to check if current authenticated user is an admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if current authenticated user is an agent or admin
CREATE OR REPLACE FUNCTION is_agent_or_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = auth.uid() AND role IN ('agent', 'admin')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 1. Profiles Policies
-- ============================================================================
-- Anyone authenticated can view their own profile; agents & admins can view all profiles
CREATE POLICY "Users can view own profile" 
ON profiles FOR SELECT 
TO authenticated 
USING (auth.uid() = id OR is_agent_or_admin());

-- Users can update their own profile; admins can update any profile
CREATE POLICY "Users can update own profile" 
ON profiles FOR UPDATE 
TO authenticated 
USING (auth.uid() = id OR is_admin());

-- New users can register
CREATE POLICY "Enable insert for registration" 
ON profiles FOR INSERT 
TO anon, authenticated 
WITH CHECK (TRUE);

-- ============================================================================
-- 2. Agents Table Policies
-- ============================================================================
CREATE POLICY "Anyone authenticated can view agents info" 
ON agents FOR SELECT 
TO authenticated 
USING (TRUE);

CREATE POLICY "Agents can update their own status" 
ON agents FOR UPDATE 
TO authenticated 
USING (auth.uid() = id OR is_admin());

CREATE POLICY "Admins can manage agents" 
ON agents FOR ALL 
TO authenticated 
USING (is_admin());

-- ============================================================================
-- 3. Conversations Policies
-- ============================================================================
CREATE POLICY "Customers view own conversations, agents/admins view all" 
ON conversations FOR SELECT 
TO authenticated 
USING (customer_id = auth.uid() OR is_agent_or_admin());

CREATE POLICY "Customers can create conversations" 
ON conversations FOR INSERT 
TO authenticated 
WITH CHECK (customer_id = auth.uid() OR is_admin());

CREATE POLICY "Customers can update own conversations, agents/admins can update" 
ON conversations FOR UPDATE 
TO authenticated 
USING (customer_id = auth.uid() OR is_agent_or_admin());

-- ============================================================================
-- 4. Messages Policies
-- ============================================================================
CREATE POLICY "View messages if user has access to conversation" 
ON messages FOR SELECT 
TO authenticated 
USING (
    EXISTS (
        SELECT 1 FROM conversations c 
        WHERE c.id = messages.conversation_id 
        AND (c.customer_id = auth.uid() OR is_agent_or_admin())
    )
);

CREATE POLICY "Insert messages into accessible conversation" 
ON messages FOR INSERT 
TO authenticated 
WITH CHECK (
    EXISTS (
        SELECT 1 FROM conversations c 
        WHERE c.id = messages.conversation_id 
        AND (c.customer_id = auth.uid() OR is_agent_or_admin())
    )
);

-- ============================================================================
-- 5. Tickets Policies
-- ============================================================================
CREATE POLICY "Customers view own tickets, agents view assigned, admins view all" 
ON tickets FOR SELECT 
TO authenticated 
USING (
    customer_id = auth.uid() 
    OR assigned_agent_id = auth.uid() 
    OR is_agent_or_admin()
);

CREATE POLICY "Customers can create support tickets" 
ON tickets FOR INSERT 
TO authenticated 
WITH CHECK (customer_id = auth.uid() OR is_agent_or_admin());

CREATE POLICY "Agents and admins can update tickets" 
ON tickets FOR UPDATE 
TO authenticated 
USING (
    assigned_agent_id = auth.uid() 
    OR is_agent_or_admin()
);

-- ============================================================================
-- 6. Ticket Notes Policies
-- ============================================================================
CREATE POLICY "Agents and admins can view ticket notes; customers view non-internal" 
ON ticket_notes FOR SELECT 
TO authenticated 
USING (
    is_agent_or_admin() 
    OR (
        is_internal = FALSE 
        AND EXISTS (
            SELECT 1 FROM tickets t 
            WHERE t.id = ticket_notes.ticket_id AND t.customer_id = auth.uid()
        )
    )
);

CREATE POLICY "Agents and admins can insert ticket notes" 
ON ticket_notes FOR INSERT 
TO authenticated 
WITH CHECK (is_agent_or_admin());

-- ============================================================================
-- 7. Knowledge Documents & Chunks Policies
-- ============================================================================
CREATE POLICY "Anyone authenticated can view knowledge documents" 
ON knowledge_documents FOR SELECT 
TO authenticated, anon 
USING (TRUE);

CREATE POLICY "Only admins can manage knowledge documents" 
ON knowledge_documents FOR ALL 
TO authenticated 
USING (is_admin());

CREATE POLICY "Anyone authenticated can search document chunks" 
ON document_chunks FOR SELECT 
TO authenticated, anon 
USING (TRUE);

CREATE POLICY "Only admins can manage document chunks" 
ON document_chunks FOR ALL 
TO authenticated 
USING (is_admin());

-- ============================================================================
-- 8. FAQs Policies
-- ============================================================================
CREATE POLICY "Public can view active FAQs" 
ON faqs FOR SELECT 
TO authenticated, anon 
USING (is_active = TRUE OR is_agent_or_admin());

CREATE POLICY "Only admins can manage FAQs" 
ON faqs FOR ALL 
TO authenticated 
USING (is_admin());

-- ============================================================================
-- 9. Feedback Policies
-- ============================================================================
CREATE POLICY "Customers can submit feedback" 
ON feedback FOR INSERT 
TO authenticated 
WITH CHECK (customer_id = auth.uid());

CREATE POLICY "Agents and admins can view feedback" 
ON feedback FOR SELECT 
TO authenticated 
USING (customer_id = auth.uid() OR is_agent_or_admin());

-- ============================================================================
-- 10. Notifications Policies
-- ============================================================================
CREATE POLICY "Users can view and manage their own notifications" 
ON notifications FOR ALL 
TO authenticated 
USING (user_id = auth.uid());
