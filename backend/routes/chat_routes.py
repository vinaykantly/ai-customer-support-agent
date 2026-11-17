import uuid
from flask import Blueprint, request, jsonify, current_app
from backend.middleware.auth_middleware import token_required
from backend.middleware.security import detect_prompt_injection, sanitize_text
from backend.middleware.rate_limiter import rate_limit, chat_limiter
from backend.services.sentiment_service import SentimentService

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

@chat_bp.route("/message", methods=["POST"])
@rate_limit(chat_limiter)
def send_message():
    data = request.get_json() or {}
    raw_message = data.get("message", "")
    session_id = data.get("session_id") or f"sess_{uuid.uuid4().hex[:12]}"
    language = data.get("language", "en")
    customer_id = data.get("customer_id")

    if not raw_message.strip():
        return jsonify({"error": "Bad Request", "message": "Message content cannot be empty."}), 400

    # Prompt Injection & Jailbreak Defense
    is_injected, matched_pattern = detect_prompt_injection(raw_message)
    if is_injected:
        return jsonify({
            "message": {
                "content": "Security Notice: Your query triggered our safety guardrails and cannot be processed. Please ask legitimate customer support questions.",
                "sender_type": "bot",
                "sentiment": "NEUTRAL",
                "intent": "SECURITY_VIOLATION",
                "sources": [],
                "language": language,
                "suggest_escalation": False
            }
        }), 200

    message_content = sanitize_text(raw_message)
    db = current_app.config["DB_MANAGER"]
    rag_service = current_app.config["RAG_SERVICE"]

    # Retrieve or create conversation
    conv = db.get_or_create_conversation(
        session_id=session_id,
        customer_id=customer_id,
        language=language,
        title=message_content[:50] + ("..." if len(message_content) > 50 else "")
    )
    conversation_id = conv["id"]

    # Analyze intent and sentiment
    intent = SentimentService.analyze_intent(message_content)
    sentiment = SentimentService.analyze_sentiment(message_content)

    # Save user message
    db.add_message(
        conversation_id=conversation_id,
        sender_type="user",
        content=message_content,
        intent=intent,
        sentiment=sentiment,
        language=language
    )

    # Fetch recent conversation history
    history = db.get_messages(conversation_id)

    # RAG Retrieval and Answer Generation
    rag_result = rag_service.retrieve_and_generate(
        user_message=message_content,
        conversation_history=history,
        language=language
    )

    bot_reply = rag_result["answer"]
    sources = rag_result.get("sources", [])

    # Check escalation threshold
    suggest_escalation = SentimentService.should_suggest_escalation(
        message=message_content,
        sentiment=sentiment,
        intent=intent
    )

    # If explicit escalation request, prepend escalation guidance
    if intent == "ESCALATION_REQUEST":
        suggest_escalation = True
        if language == "kn":
            bot_reply += "\n\nನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ಮಾನವ ತಜ್ಞರೊಂದಿಗೆ ಪರಿಹರಿಸಲು ಕೆಳಗಿನ 'ಎಸ್ಕೆಲೇಟ್ ಟು ಏಜೆಂಟ್' ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ."
        elif language == "hi":
            bot_reply += "\n\nआपकी समस्या के तुरंत समाधान के लिए कृपया नीचे दिए गए 'मानव एजेंट से संपर्क करें' बटन पर क्लिक करें।"
        else:
            bot_reply += "\n\nClick the 'Escalate to Human Agent' button below to transfer your issue and transcript directly to a support specialist."

    # Save bot message
    saved_bot_msg = db.add_message(
        conversation_id=conversation_id,
        sender_type="bot",
        content=bot_reply,
        intent=intent,
        sentiment=sentiment,
        sources=sources,
        language=language
    )

    return jsonify({
        "session_id": session_id,
        "conversation_id": conversation_id,
        "message": saved_bot_msg,
        "sentiment": sentiment,
        "intent": intent,
        "suggest_escalation": suggest_escalation
    }), 200

@chat_bp.route("/conversations", methods=["GET"])
@token_required
def get_user_conversations():
    db = current_app.config["DB_MANAGER"]
    convs = db.get_user_conversations(request.current_user["id"])
    return jsonify({"conversations": convs}), 200

@chat_bp.route("/conversations/<conv_id>", methods=["GET"])
def get_conversation_history(conv_id):
    db = current_app.config["DB_MANAGER"]
    conv = db.get_conversation_by_id(conv_id)
    if not conv:
        return jsonify({"error": "Not Found", "message": "Conversation not found."}), 404
        
    messages = db.get_messages(conv_id)
    return jsonify({
        "conversation": conv,
        "messages": messages
    }), 200

@chat_bp.route("/suggested-questions", methods=["GET"])
def get_suggested_questions():
    language = request.args.get("language", "en")
    suggestions = {
        "en": [
            "What is your refund policy?",
            "How do I reset my password?",
            "What are your human support operating hours?",
            "How do I escalate my issue to a human agent?",
            "What is your ticket resolution SLA?"
        ],
        "kn": [
            "ನಿಮ್ಮ ಮರುಪಾವತಿ ನೀತಿ ಏನು?",
            "ನನ್ನ ಪಾಸ್‌ವರ್ಡ್ ಅನ್ನು ಮರುಹೊಂದಿಸುವುದು ಹೇಗೆ?",
            "ನಿಮ್ಮ ಬೆಂಬಲ ಕಾರ್ಯಾಚರಣೆಯ ಸಮಯಗಳು ಯಾವುವು?",
            "ನನ್ನ ಸಮಸ್ಯೆಯನ್ನು ಮಾನವ ಏಜೆಂಟ್‌ಗೆ ವರ್ಗಾಯಿಸುವುದು ಹೇಗೆ?"
        ],
        "hi": [
            "आपकी रिफंड नीति क्या है?",
            "मैं अपना पासवर्ड कैसे रीसेट करूं?",
            "आपके सहायता सेवा के संचालन का समय क्या है?",
            "मैं मानव एजेंट से कैसे बात कर सकता हूँ?"
        ]
    }
    return jsonify({"questions": suggestions.get(language, suggestions["en"])}), 200

@chat_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json() or {}
    rating = data.get("rating")
    comment = sanitize_text(data.get("comment", ""))
    conversation_id = data.get("conversation_id")
    ticket_id = data.get("ticket_id")
    customer_id = data.get("customer_id")

    if not rating or not (1 <= int(rating) <= 5):
        return jsonify({"error": "Bad Request", "message": "Rating between 1 and 5 is required."}), 400

    db = current_app.config["DB_MANAGER"]
    fb = db.add_feedback(
        customer_id=customer_id,
        rating=int(rating),
        comment=comment,
        conversation_id=conversation_id,
        ticket_id=ticket_id
    )
    return jsonify({"message": "Thank you for your feedback!", "feedback": fb}), 201

@chat_bp.route("/escalate", methods=["POST"])
def escalate_conversation():
    data = request.get_json() or {}
    conversation_id = data.get("conversation_id")
    customer_id = data.get("customer_id")
    title = sanitize_text(data.get("title", "Escalated Support Ticket from AI Chat"))
    category = data.get("category", "GENERAL")
    priority = data.get("priority", "HIGH")

    db = current_app.config["DB_MANAGER"]
    conv = db.get_conversation_by_id(conversation_id) if conversation_id else None

    # Compile conversation transcript
    description = "Escalated from AI Chatbot Session.\n\n"
    if conv:
        customer_id = customer_id or conv.get("customer_id")
        messages = db.get_messages(conversation_id)
        description += "--- Conversation Transcript ---\n"
        for m in messages[-8:]:
            sender = "User" if m["sender_type"] == "user" else "AI Assistant"
            description += f"[{sender}]: {m['content']}\n"
    else:
        description += data.get("description", "Customer requested escalation to a human agent.")

    if not customer_id:
        # Default customer if guest
        customer_id = "c0000000-0000-0000-0000-000000000001"

    ticket = db.create_ticket(
        customer_id=customer_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        conversation_id=conversation_id
    )

    # Update conversation status
    if conversation_id:
        db.update_conversation(conversation_id, status="ESCALATED")

    return jsonify({
        "message": f"Successfully escalated to ticket {ticket['ticket_number']}.",
        "ticket": ticket
    }), 201
