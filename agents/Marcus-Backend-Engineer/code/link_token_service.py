"""
Link token service: create, verify, consume. Uses HMAC-SHA256 for hashing and constant-time compare.
Note: HMAC secret must be provided from a secure secret store (Vault) in production.
"""
import hmac
import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from ..models.link_token import LinkToken


HMAC_SECRET = os.environ.get("LINK_TOKEN_HMAC_SECRET", "dev-secret-please-change")
HASH_ALGO = "sha256"
TOKEN_BYTE_LEN = 32


def _hmac_hash(token: str) -> str:
    """Return hex HMAC-SHA256 of token using secret."""
    if isinstance(HMAC_SECRET, str):
        key = HMAC_SECRET.encode()
    else:
        key = HMAC_SECRET
    h = hmac.new(key, token.encode(), hashlib.sha256)
    return h.hexdigest()


def _constant_time_compare(a: str, b: str) -> bool:
    """Wrapper around hmac.compare_digest for constant-time compare"""
    return hmac.compare_digest(a, b)


def create_link_token(
    db: Session,
    owner_id,
    allowed_emails: Optional[list] = None,
    ttl_seconds: int = 3600,
    single_use: bool = False,
    metadata: Optional[dict] = None,
):
    """Create a link token record and return the raw token string to embed in links.

    Important: only the HMAC hash of the token is stored in DB.
    """
    raw_token = secrets.token_urlsafe(TOKEN_BYTE_LEN)
    token_hash = _hmac_hash(raw_token)
    expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)

    lt = LinkToken(
        token_hash=token_hash,
        owner_id=owner_id,
        allowed_emails=allowed_emails,
        expiry=expiry,
        single_use=single_use,
        metadata=metadata,
    )
    db.add(lt)
    db.commit()
    db.refresh(lt)
    return raw_token, lt


def verify_link_token(db: Session, raw_token: str, now: Optional[datetime] = None) -> Optional[LinkToken]:
    """Verify token by computing HMAC and searching DB. Returns LinkToken if valid and not revoked/expired.

    This function deliberately queries by token_hash to avoid retrieving many rows.
    """
    now = now or datetime.utcnow()
    token_hash = _hmac_hash(raw_token)
    # Query by token_hash
    lt = db.query(LinkToken).filter_by(token_hash=token_hash).first()
    if not lt:
        return None
    if lt.revoked:
        return None
    if lt.expiry <= now:
        return None
    # Allowed emails and owner checks should be done by caller
    return lt


def consume_link_token(db: Session, lt: LinkToken) -> bool:
    """Mark single-use token as revoked/consumed. Returns True on success."""
    if not lt.single_use:
        return True
    lt.revoked = True
    db.add(lt)
    db.commit()
    return True
