# Filename: output/code/security/auth_middleware.py

"""
Authentication & Authorization middleware snippets and utilities for Investor Portal.
- Token hashing/validation
- RBAC check example
- Rate-limiting hooks (stubs)

NOT production-ready. Intended as security-focused implementation guidance to integrate into backend.
"""

from typing import Optional
import hashlib
import hmac
import base64
import os
import time

# Configuration (should be provided from secure secrets manager)
HMAC_KEY = os.environ.get('LINK_HMAC_KEY', 'dev-placeholder-key')
TOKEN_MIN_ENTROPY_BYTES = 32  # 256 bits


def hash_token(token: str, key: Optional[bytes] = None) -> str:
    """Return hex HMAC-SHA256 of token using server-side key."""
    if key is None:
        key = HMAC_KEY.encode('utf-8')
    return hmac.new(key, token.encode('utf-8'), hashlib.sha256).hexdigest()


def constant_time_compare(val1: str, val2: str) -> bool:
    """Constant time comparison to avoid timing attacks."""
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1.encode('utf-8'), val2.encode('utf-8')):
        result |= x ^ y
    return result == 0


def generate_token(nbytes: int = TOKEN_MIN_ENTROPY_BYTES) -> str:
    """Generate a URL-safe token with >=256 bits entropy."""
    raw = os.urandom(nbytes)
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('utf-8')


# Example authorization check (should be integrated into request lifecycle)

def authorize_request(user_id: Optional[int], resource_owner_id: int, token_hash: Optional[str], action: str) -> bool:
    """Basic authorize: allow if user is owner or token_hash valid and not expired.
    This is a placeholder; replace with DB checks and RBAC.
    """
    # If authenticated owner
    if user_id is not None and user_id == resource_owner_id:
        return True

    # Otherwise check token-based access (token_hash validation should be done prior)
    if token_hash:
        # Here we'd check expiry and revocation status from DB
        # For demo, assume token is valid
        return True

    return False


# Rate limit stub
class RateLimiter:
    def __init__(self):
        self.store = {}

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = int(time.time())
        window = now // window_seconds
        k = f"{key}:{window}"
        self.store.setdefault(k, 0)
        if self.store[k] >= limit:
            return False
        self.store[k] += 1
        return True


# Example usage comments
# - On link creation: token = generate_token(); store hash_token(token) in DB with metadata
# - On link access: receive token from URL path (not query param), compute hash and compare constant_time_compare
# - Enforce single-use by marking revoked upon successful consumption if single_use=True

