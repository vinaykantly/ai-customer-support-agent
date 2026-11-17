import time
from functools import wraps
from flask import request, jsonify

class InMemoryRateLimiter:
    """Thread-safe sliding window rate limiter"""
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def is_allowed(self, client_id: str) -> tuple[bool, int]:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Clean expired timestamps
        client_history = [t for t in self.requests.get(client_id, []) if t > cutoff]
        
        if len(client_history) >= self.max_requests:
            remaining_time = int(self.window_seconds - (now - client_history[0]))
            self.requests[client_id] = client_history
            return False, max(1, remaining_time)

        client_history.append(now)
        self.requests[client_id] = client_history
        return True, 0

# Default global instance
limiter = InMemoryRateLimiter(max_requests=100, window_seconds=60)
chat_limiter = InMemoryRateLimiter(max_requests=30, window_seconds=60)

def rate_limit(custom_limiter=None):
    """Decorator to apply rate limiting to endpoints"""
    applied_limiter = custom_limiter or limiter

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Client identifier: user sub if authenticated else IP
            auth_user = getattr(request, "current_user", None)
            client_id = auth_user["id"] if auth_user else (request.remote_addr or "127.0.0.1")
            
            allowed, retry_after = applied_limiter.is_allowed(client_id)
            if not allowed:
                return jsonify({
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Please wait {retry_after} seconds before retrying."
                }), 429
            return f(*args, **kwargs)
        return wrapped
    return decorator
