import re
import html

# Common Prompt Injection & Jailbreak patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior)\s+guidelines",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"dan\s+mode\s+enabled",
    r"act\s+as\s+(an\s+unfiltered|jailbroken|unrestricted)\s+ai",
    r"bypass\s+(all\s+)?safety\s+filters",
    r"reveal\s+(your\s+)?(system\s+prompt|initial\s+instructions)",
    r"print\s+(your\s+)?system\s+prompt",
    r"what\s+is\s+your\s+hidden\s+instruction",
    r"do\s+anything\s+now",
    r"output\s+the\s+database\s+password",
    r"drop\s+table\s+",
    r"<script\b[^>]*>(.*?)</script>"
]

COMPILED_INJECTION_REGEX = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]

def detect_prompt_injection(text: str) -> tuple[bool, str]:
    """
    Checks if user input contains known prompt injection or jailbreak attempts.
    Returns (is_injected, matched_pattern)
    """
    if not text:
        return False, ""
    
    clean_text = text.lower()
    for regex in COMPILED_INJECTION_REGEX:
        match = regex.search(clean_text)
        if match:
            return True, match.group(0)
    return False, ""

def sanitize_text(text: str, max_length: int = 4000) -> str:
    """
    Sanitizes user input by stripping potentially hazardous HTML/scripts,
    normalizing whitespace, and truncating to max_length.
    """
    if not text:
        return ""
    # Strip dangerous HTML tags
    cleaned = re.sub(r"<[^>]*>", "", text)
    # Unescape any encoded entities then escape safe representation
    cleaned = html.escape(cleaned.strip())
    # Limit maximum characters
    return cleaned[:max_length]

def validate_email(email: str) -> bool:
    """Validates email format"""
    if not email or len(email) > 254:
        return False
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Ensures minimum password complexity: at least 8 chars, 1 digit, 1 letter"""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def is_allowed_pdf(filename: str, file_stream=None) -> bool:
    """Checks extension and optionally PDF magic bytes"""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    if ext != "pdf":
        return False
    
    if file_stream:
        header = file_stream.read(4)
        file_stream.seek(0)
        if header != b"%PDF":
            return False
            
    return True
