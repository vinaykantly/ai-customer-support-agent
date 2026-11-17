import json
import requests

SYSTEM_INSTRUCTION = """
You are an intelligent, empathetic, and professional AI Customer Support Agent for our enterprise platform.
Your objective is to help customers resolve inquiries, understand policies, troubleshoot technical issues, and ensure customer satisfaction.

CRITICAL OPERATIONAL RULES:
1. STRICT GROUNDING: Answer questions based solely on the provided Knowledge Base Context and FAQs.
2. NEVER FABRICATE: Never invent company policies, pricing plans, transaction records, bank confirmations, or refund approvals. If information is not in the provided context, state politely: "I do not have sufficient information in our official knowledge base to confirm this detail. Would you like me to connect you with a human support agent?"
3. NEVER ISSUE DIRECT REFUNDS: You cannot directly trigger payment refunds or financial credits. Direct the customer to open a Billing support ticket or offer to escalate.
4. MULTILINGUAL SUPPORT:
   - If the user writes in English, reply in English.
   - If the user writes in Kannada (ಕನ್ನಡ), reply in natural, polite Kannada.
   - If the user writes in Hindi (हिन्दी), reply in natural, polite Hindi.
   - If a target language is explicitly provided, prioritize that language.
5. SOURCE CITATIONS: Whenever using information from the context, mention the source document name (e.g., "[Source: Company Support Policy & SLA Manual]").
6. TONE: Empathetic, helpful, concise, and reassuring.
"""

class GeminiService:
    """
    Connects to Google Gemini API for context-grounded conversational AI.
    Handles multilingual translation, prompt guardrails, and offline synthesis fallback.
    """
    def __init__(self, api_key: str = "", model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_response(self, user_message: str, context_chunks: list[dict], conversation_history: list[dict] = None, target_language: str = "en") -> dict:
        """
        Generates grounded conversational answer.
        Returns:
        {
            "answer": str,
            "sources": list[dict],
            "language": str,
            "grounded": bool
        }
        """
        sources = []
        context_str = ""
        for idx, chunk in enumerate(context_chunks):
            doc_title = chunk.get("doc_title") or chunk.get("metadata", {}).get("doc_title", "Official Support Document")
            context_str += f"\n--- Source Document [{idx+1}]: {doc_title} ---\n{chunk.get('content', '')}\n"
            sources.append({
                "title": doc_title,
                "section": chunk.get("metadata", {}).get("section", f"Chunk {chunk.get('chunk_index', idx+1)}"),
                "similarity": chunk.get("similarity", 0.8)
            })

        # If API key is available, call Gemini REST API
        if self.api_key:
            try:
                response = self._call_gemini_api(user_message, context_str, conversation_history, target_language)
                if response:
                    return {
                        "answer": response,
                        "sources": sources,
                        "language": target_language,
                        "grounded": len(sources) > 0
                    }
            except Exception as e:
                print(f"[GeminiService] API generation failed: {e}. Falling back to grounded local response.")

        # Local Grounded Synthesis Fallback
        local_answer = self._generate_local_fallback(user_message, context_chunks, target_language)
        return {
            "answer": local_answer,
            "sources": sources,
            "language": target_language,
            "grounded": len(sources) > 0
        }

    def _call_gemini_api(self, user_message: str, context_str: str, history: list[dict], target_language: str) -> str:
        """Invokes Gemini 1.5 Flash / 2.0 REST API"""
        contents = []

        # Format past conversation history (up to last 6 turns)
        if history:
            for msg in history[-6:]:
                role = "user" if msg.get("sender_type") == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.get("content", "")}]
                })

        # Append current user prompt with context and instruction
        lang_note = {
            "en": "Respond in English.",
            "kn": "Respond in Kannada (ಕನ್ನಡ).",
            "hi": "Respond in Hindi (हिन्दी)."
        }.get(target_language, "Respond in English.")

        prompt_text = f"""
Knowledge Base Context:
{context_str if context_str else "No specific knowledge base documents retrieved for this inquiry."}

Target Language Requirement: {lang_note}

Customer Message:
{user_message}
"""
        contents.append({
            "role": "user",
            "parts": [{"text": prompt_text}]
        })

        payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 800,
                "topP": 0.85
            }
        }

        resp = requests.post(f"{self.endpoint}?key={self.api_key}", json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
        else:
            print(f"[GeminiService] API Error {resp.status_code}: {resp.text}")

        return None

    def _generate_local_fallback(self, user_message: str, context_chunks: list[dict], language: str) -> str:
        """
        Synthesizes an accurate grounded response locally when operating in offline/demo mode.
        """
        msg_lower = user_message.lower()

        # Multilingual greetings
        if any(w in msg_lower for w in ["hello", "hi", "hey", "namaste", "ನಮಸ್ಕಾರ", "नमस्ते"]):
            if language == "kn":
                return "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಎಐ ಗ್ರಾಹಕ ಬೆಂಬಲ ಸಹಾಯಕ. ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
            elif language == "hi":
                return "नमस्ते! मैं आपका एआई ग्राहक सहायता सहायक हूँ। आज मैं आपकी क्या मदद कर सकता हूँ?"
            return "Hello! I am your AI Customer Support Assistant. How can I help you today?"

        # If relevant knowledge base context was retrieved
        if context_chunks:
            top_chunk = context_chunks[0]
            content = top_chunk.get("content", "")
            title = top_chunk.get("doc_title") or "Official Support Document"

            if language == "kn":
                return f"ನಮ್ಮ ಅಧಿಕೃತ ನೀತಿ ದಾಖಲೆಯ ಪ್ರಕಾರ ({title}):\n\n{content}\n\nಹೆಚ್ಚಿನ ವಿವರಗಳಿಗಾಗಿ ನೀವು ಬೆಂಬಲ ಟಿಕೆಟ್ ರಚಿಸಬಹುದು ಅಥವಾ ಮಾನವ ಪ್ರತಿನಿಧಿಯೊಂದಿಗೆ ಮಾತನಾಡಬಹುದು."
            elif language == "hi":
                return f"हमारे आधिकारिक नीति दस्तावेज़ ({title}) के अनुसार:\n\n{content}\n\nयदि आपके कोई अन्य प्रश्न हैं, तो आप सहायता टिकट बना सकते हैं या मानव एजेंट से बात कर सकते हैं।"
            return f"According to our {title}:\n\n{content}\n\nIf you need further assistance or specific account adjustments, please feel free to create a support ticket or request human escalation."

        # Default fallback when no document chunk matches
        if language == "kn":
            return "ನಮ್ಮ ಜ್ಞಾನ ಭಂಡಾರದಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ನೇರ ಉತ್ತರ ಕಂಡುಬಂದಿಲ್ಲ. ನೀವು ಬೆಂಬಲ ಟಿಕೆಟ್ ರಚಿಸಲು ಬಯಸುವಿರಾ ಅಥವಾ ಮಾನವ ಬೆಂಬಲ ಏಜೆಂಟ್‌ಗೆ ಸಂಪರ್ಕಿಸಲು ಬಯಸುವಿರಾ?"
        elif language == "hi":
            return "हमारे नॉलेज बेस में इस प्रश्न के लिए पर्याप्त जानकारी नहीं मिली है। क्या आप चाहते हैं कि मैं आपके लिए एक सहायता टिकट बनाऊं या किसी मानव एजेंट से संपर्क कराऊं?"
        return "I do not have specific information in our official company knowledge base for this inquiry. Would you like me to create a support ticket or escalate this to a human support agent?"
