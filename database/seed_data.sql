-- ============================================================================
-- AI-POWERED CUSTOMER SUPPORT AGENT
-- Seed Data Script
-- File: database/seed_data.sql
-- ============================================================================

-- 1. Insert User Profiles
-- Passwords:
-- Admin: Admin@123
-- Agents: Agent@123
-- Customer: Customer@123
INSERT INTO profiles (id, email, password_hash, full_name, role, phone, is_active)
VALUES
    ('a0000000-0000-0000-0000-000000000001', 'admin@company.com', 'scrypt:32768:8:1$GypVErHbZ3qOczXa$872da243719b304ea243f4b4535de00722909d5ccdeead7fb5108e6ff599aee416dd2c146f80ddee882cb8f49d45bab17514b89e17ec44e830ac1147926b337c', 'System Administrator', 'admin', '+1-800-555-0100', TRUE),
    ('b0000000-0000-0000-0000-000000000001', 'agent.rajesh@company.com', 'scrypt:32768:8:1$D2hTnuVFhbfh9SOG$11532a5c10433682d599b643eaf647478890d92bcf01247b731e3274bb3d74b103fb77b3cab3405ad2e21107cfabe749aca66a6be0f3acac40768e693074a960', 'Rajesh Sharma', 'agent', '+1-800-555-0101', TRUE),
    ('b0000000-0000-0000-0000-000000000002', 'agent.priya@company.com', 'scrypt:32768:8:1$D2hTnuVFhbfh9SOG$11532a5c10433682d599b643eaf647478890d92bcf01247b731e3274bb3d74b103fb77b3cab3405ad2e21107cfabe749aca66a6be0f3acac40768e693074a960', 'Priya Patel', 'agent', '+1-800-555-0102', TRUE),
    ('c0000000-0000-0000-0000-000000000001', 'customer@example.com', 'scrypt:32768:8:1$DyQaeczCNMZmVq2J$36a8775feceb8a7f5a800690663d5e153bd1ec840b214c5d3cf2a98b69443d5c7238f2b8dfb753789953dad27c6a83655a14e3a60c3659ef2ec7de49987a706a', 'Ananya Roy', 'customer', '+1-800-555-0199', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 2. Insert Agent Details
INSERT INTO agents (id, department, is_available, max_tickets, current_tickets_count, skills)
VALUES
    ('b0000000-0000-0000-0000-000000000001', 'Billing & Finance', TRUE, 5, 1, ARRAY['Billing', 'Refunds', 'Subscriptions', 'Hindi']),
    ('b0000000-0000-0000-0000-000000000002', 'Technical Support', TRUE, 5, 1, ARRAY['API', 'Cloud Integration', 'Authentication', 'Kannada', 'Hindi'])
ON CONFLICT (id) DO NOTHING;

-- 3. Insert FAQs
INSERT INTO faqs (id, question, answer, category, is_active)
VALUES
    ('d0000000-0000-0000-0000-000000000001', 'What is your refund policy?', 'We offer a full 30-day money-back guarantee for all annual and monthly subscription plans if requested within 30 days of the transaction date. Please contact billing support with your invoice ID.', 'BILLING', TRUE),
    ('d0000000-0000-0000-0000-000000000002', 'How do I reset my account password?', 'You can reset your account password by navigating to the Profile page or clicking "Forgot Password" on the login screen. An automated verification code will be sent to your registered email.', 'ACCOUNT', TRUE),
    ('d0000000-0000-0000-0000-000000000003', 'What are your support operating hours?', 'Our AI customer support assistant operates 24/7/365. Human support agents are available Monday through Saturday from 9:00 AM to 8:00 PM IST.', 'GENERAL', TRUE),
    ('d0000000-0000-0000-0000-000000000004', 'What languages does the AI assistant support?', 'The assistant natively supports English, Kannada (ಕನ್ನಡ), and Hindi (हिन्दी). You can switch languages dynamically using the language selector or typing directly in your preferred language.', 'TECHNICAL', TRUE),
    ('d0000000-0000-0000-0000-000000000005', 'How do I escalate my issue to a human agent?', 'Simply click the "Escalate to Human Agent" button inside the chat window, or type "I want to talk to an agent". A support ticket will be immediately generated and queued for assignment.', 'GENERAL', TRUE),
    ('d0000000-0000-0000-0000-000000000006', 'What is the standard SLA for ticket resolution?', 'Urgent tickets are acknowledged within 1 hour. High priority issues within 4 hours. Medium and Low priority tickets are addressed within 24 business hours.', 'GENERAL', TRUE),
    ('d0000000-0000-0000-0000-000000000007', 'How do I upgrade my subscription plan?', 'Navigate to Account Settings > Billing & Plans, select your desired tier (Starter, Pro, Enterprise), and proceed through the secure checkout portal.', 'BILLING', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 4. Insert Sample Knowledge Document
INSERT INTO knowledge_documents (id, title, file_name, file_path, file_size, mime_type, chunk_count, status, uploaded_by)
VALUES
    ('e0000000-0000-0000-0000-000000000001', 'Official Company Support Policy & SLA Manual', 'support_policy_v2.pdf', 'uploads/support_policy_v2.pdf', 245760, 'application/pdf', 3, 'PROCESSED', 'a0000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- 5. Insert Sample Knowledge Document Chunks
INSERT INTO document_chunks (id, document_id, chunk_index, content, metadata)
VALUES
    ('f0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 1, 
    'Section 1: General Support SLA & Escalation. Our customer service tier provides 24/7 AI-first triage. If a customer query cannot be answered or if the customer expresses frustration, the system automatically tags the conversation as ESCALATED and opens a Priority Medium or High ticket depending on business impact.',
    '{"page": 1, "section": "1.1", "doc_title": "Official Company Support Policy & SLA Manual"}'::jsonb),
    ('f0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000001', 2, 
    'Section 2: Refund and Billing Dispute Standards. Customers may request a refund within thirty (30) calendar days from payment confirmation. Refunds require human agent verification of the payment gateway transaction ID. AI bots are strictly barred from committing to refunds or executing account credits without agent approval.',
    '{"page": 2, "section": "2.3", "doc_title": "Official Company Support Policy & SLA Manual"}'::jsonb),
    ('f0000000-0000-0000-0000-000000000003', 'e0000000-0000-0000-0000-000000000001', 3, 
    'Section 3: Security, Privacy, and Authentication. Multi-factor authentication is enforced for all Agent and Admin sessions. Customer data is encrypted at rest using AES-256 and in transit via TLS 1.3. Passwords must be at least 8 characters long containing alphanumeric and special symbols.',
    '{"page": 3, "section": "3.1", "doc_title": "Official Company Support Policy & SLA Manual"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- 6. Insert Sample Conversation
INSERT INTO conversations (id, customer_id, session_id, title, language, sentiment, status)
VALUES
    ('c1000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'sess_demo_001', 'Inquiry regarding Refund Policy', 'en', 'NEUTRAL', 'ACTIVE')
ON CONFLICT (id) DO NOTHING;

-- 7. Insert Sample Chat Messages
INSERT INTO messages (id, conversation_id, sender_type, content, intent, sentiment, sources, language)
VALUES
    ('m0000000-0000-0000-0000-000000000001', 'c1000000-0000-0000-0000-000000000001', 'user', 'Hi, can you explain your refund policy?', 'BILLING_INQUIRY', 'NEUTRAL', '[]'::jsonb, 'en'),
    ('m0000000-0000-0000-0000-000000000002', 'c1000000-0000-0000-0000-000000000001', 'bot', 'According to our Official Company Support Policy, you can request a full refund within 30 calendar days from your payment confirmation date. Please note that refund processing requires verification by our billing support team.', 'BILLING_INQUIRY', 'POSITIVE', '[{"title": "Official Company Support Policy & SLA Manual", "section": "2.3"}]'::jsonb, 'en')
ON CONFLICT (id) DO NOTHING;

-- 8. Insert Sample Tickets Across Various Statuses
INSERT INTO tickets (id, ticket_number, customer_id, conversation_id, title, description, category, priority, status, assigned_agent_id)
VALUES
    ('t0000000-0000-0000-0000-000000000001', 'TIK-20261115-A101', 'c0000000-0000-0000-0000-000000000001', 'c1000000-0000-0000-0000-000000000001', 
    'Subscription charge duplicate on credit card', 
    'Customer noticed two identical charges of $49 on their card for the monthly subscription.', 
    'BILLING', 'HIGH', 'IN_PROGRESS', 'b0000000-0000-0000-0000-000000000001'),

    ('t0000000-0000-0000-0000-000000000002', 'TIK-20261115-B202', 'c0000000-0000-0000-0000-000000000001', NULL, 
    'API Rate Limit error 429 during batch sync', 
    'Our nightly sync job hit the 429 error code multiple times around 2 AM UTC.', 
    'TECHNICAL', 'MEDIUM', 'OPEN', 'b0000000-0000-0000-0000-000000000002'),

    ('t0000000-0000-0000-0000-000000000003', 'TIK-20261114-C303', 'c0000000-0000-0000-0000-000000000001', NULL, 
    'SSO Integration certificate expiration warning', 
    'Okta SAML certificate is due to expire in 5 days. Need verification of renewed cert.', 
    'TECHNICAL', 'URGENT', 'ESCALATED', 'b0000000-0000-0000-0000-000000000002'),

    ('t0000000-0000-0000-0000-000000000004', 'TIK-20261110-D404', 'c0000000-0000-0000-0000-000000000001', NULL, 
    'Invoice address update for Q4 audit', 
    'Updated company legal entity address for upcoming fiscal year invoices.', 
    'ACCOUNT', 'LOW', 'RESOLVED', 'b0000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- 9. Insert Sample Ticket Notes
INSERT INTO ticket_notes (id, ticket_id, author_id, note, is_internal)
VALUES
    ('n0000000-0000-0000-0000-000000000001', 't0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 
    'Verified Stripe payment logs. Found duplicate webhook callback. Processing $49 credit immediately.', TRUE),
    ('n0000000-0000-0000-0000-000000000002', 't0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000001', 
    'Hello Ananya, we identified the duplicate charge from our gateway provider and have triggered a $49 refund back to your payment card.', FALSE)
ON CONFLICT (id) DO NOTHING;

-- 10. Insert Sample Feedback
INSERT INTO feedback (id, conversation_id, ticket_id, customer_id, rating, comment)
VALUES
    ('fb000000-0000-0000-0000-000000000001', 'c1000000-0000-0000-0000-000000000001', NULL, 'c0000000-0000-0000-0000-000000000001', 5, 'Quick and very clear answer about refund policies!'),
    ('fb000000-0000-0000-0000-000000000002', NULL, 't0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000001', 5, 'Resolved my invoice address quickly.')
ON CONFLICT (id) DO NOTHING;

-- 11. Insert Sample Notification
INSERT INTO notifications (id, user_id, title, message, type, link)
VALUES
    ('nt000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 'Ticket Update: TIK-20261115-A101', 'Agent Rajesh Sharma has replied to your ticket regarding duplicate charges.', 'TICKET_UPDATE', '/customer_tickets.html')
ON CONFLICT (id) DO NOTHING;
