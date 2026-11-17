class RAGService:
    """
    Retrieval-Augmented Generation (RAG) Orchestrator.
    Coordinates document retrieval, vector similarity search, FAQ matching,
    and grounded synthesis via Gemini.
    """
    def __init__(self, db_manager, embedding_service, gemini_service):
        self.db = db_manager
        self.embedding_service = embedding_service
        self.gemini_service = gemini_service

    def retrieve_and_generate(self, user_message: str, conversation_history: list[dict] = None, language: str = "en") -> dict:
        """
        Executes end-to-end RAG pipeline:
        1. Embeds user query
        2. Retrieves top-k matching document chunks
        3. Retrieves matching active FAQs
        4. Synthesizes grounded answer through Gemini
        """
        # Step 1: Generate query embedding
        query_embedding = self.embedding_service.get_embedding(user_message)

        # Step 2: Retrieve top matching chunks from vector database
        matched_chunks = self.db.search_similar_chunks(
            query_embedding=query_embedding,
            match_threshold=0.25,
            match_count=4
        )

        # Step 3: Check FAQ repository for complementary context
        faqs = self.db.get_all_faqs(active_only=True)
        user_lower = user_message.lower()
        faq_context = []
        for faq in faqs:
            # Check for keyword overlap between user message and FAQ question
            q_words = set(faq["question"].lower().split())
            m_words = set(user_lower.split())
            overlap = len(q_words.intersection(m_words))
            if overlap >= 2 or any(word in user_lower for word in ["refund", "password", "hours", "sla", "language"] if word in faq["question"].lower()):
                faq_context.append({
                    "content": f"FAQ Question: {faq['question']}\nFAQ Answer: {faq['answer']}",
                    "doc_title": f"FAQ ({faq['category']})",
                    "chunk_index": 1,
                    "similarity": 0.9,
                    "metadata": {"category": faq["category"], "type": "FAQ"}
                })

        # Combine document chunks with relevant FAQs
        all_context = faq_context[:2] + matched_chunks[:3]

        # Step 4: Synthesize answer with Gemini
        ai_result = self.gemini_service.generate_response(
            user_message=user_message,
            context_chunks=all_context,
            conversation_history=conversation_history,
            target_language=language
        )

        return ai_result
