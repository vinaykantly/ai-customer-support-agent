import re

class SentimentService:
    """
    Analyzes customer messages for sentiment, intent, and escalation signals.
    Supports English, Hindi (Latin/Devanagari), and Kannada.
    """

    INTENT_KEYWORDS = {
        "REFUND_REQUEST": [
            "refund", "money back", "reimbursement", "cancel subscription", "chargeback",
            "वापसी", "रिफंड", "पैसे वापस", "ಮರುಪಾವತಿ", "ಹಣ ವಾಪಸ್"
        ],
        "BILLING_INQUIRY": [
            "billing", "invoice", "charge", "charged twice", "pricing", "payment failed",
            "credit card", "बिलिंग", "चालान", "भुगतान", "ಬಿಲ್ಲಿಂಗ್", "ಖಾತೆ"
        ],
        "TECHNICAL_SUPPORT": [
            "error", "bug", "issue", "crash", "not working", "api", "404", "500", "429", "timeout",
            "समस्या", "त्रुटि", "काम नहीं कर रहा", "ದೋಷ", "ಕೆಲಸ ಮಾಡುತ್ತಿಲ್ಲ"
        ],
        "ACCOUNT_ACCESS": [
            "password", "login", "reset", "forgot", "sso", "mfa", "2fa", "locked",
            "पासवर्ड", "लॉगिन", "ಪಾಸ್‌ವರ್ಡ್", "ಲಾಗಿನ್"
        ],
        "ESCALATION_REQUEST": [
            "talk to human", "speak to agent", "human support", "representative", "escalate",
            "customer care", "person", "manager", "human please",
            "एजेंट से बात", "मानव सहायता", "ಏಜೆಂಟ್", "ಮಾನವ ಬೆಂಬಲ"
        ]
    }

    NEGATIVE_KEYWORDS = [
        "angry", "terrible", "worst", "horrible", "awful", "scam", "cheat", "useless",
        "ridiculous", "disgusted", "frustrated", "unacceptable", "waste of money",
        "घटिया", "बेकार", "धोखा", "ಕೆಟ್ಟ", "ವ್ಯರ್ಥ"
    ]

    POSITIVE_KEYWORDS = [
        "thank", "thanks", "great", "awesome", "excellent", "helpful", "good job",
        "perfect", "love", "solved", "appreciate",
        "धन्यवाद", "बहुत अच्छा", "ಧನ್ಯವಾದಗಳು", "ಉತ್ತಮ"
    ]

    @classmethod
    def analyze_intent(cls, message: str) -> str:
        """Determines the primary intent of the customer message"""
        msg_lower = message.lower()
        
        # Check explicit escalation first
        for kw in cls.INTENT_KEYWORDS["ESCALATION_REQUEST"]:
            if kw in msg_lower:
                return "ESCALATION_REQUEST"

        for intent, keywords in cls.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in msg_lower:
                    return intent
                    
        return "GENERAL_INQUIRY"

    @classmethod
    def analyze_sentiment(cls, message: str) -> str:
        """
        Classifies sentiment as: POSITIVE, NEUTRAL, NEGATIVE, or FRUSTRATED
        """
        msg_lower = message.lower()
        
        # Check frustrated/angry cues
        neg_count = sum(1 for kw in cls.NEGATIVE_KEYWORDS if kw in msg_lower)
        if neg_count >= 2 or any(w in msg_lower for w in ["scam", "cheat", "ridiculous", "worst service"]):
            return "FRUSTRATED"
        elif neg_count == 1:
            return "NEGATIVE"

        # Check positive cues
        pos_count = sum(1 for kw in cls.POSITIVE_KEYWORDS if kw in msg_lower)
        if pos_count > 0:
            return "POSITIVE"

        return "NEUTRAL"

    @classmethod
    def should_suggest_escalation(cls, message: str, sentiment: str, intent: str, previous_failures: int = 0) -> bool:
        """
        Flags whether an automated escalation to a human agent should be offered
        """
        if intent == "ESCALATION_REQUEST":
            return True
        if sentiment == "FRUSTRATED":
            return True
        if previous_failures >= 2:
            return True
        return False
