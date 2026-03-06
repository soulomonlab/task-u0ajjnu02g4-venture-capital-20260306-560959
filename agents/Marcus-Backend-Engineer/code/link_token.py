"""
SQLAlchemy model for LinkToken (stores only hashed tokens and metadata)
"""
from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LinkToken(Base):
    __tablename__ = "link_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_hash = Column(String(128), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    allowed_emails = Column(ARRAY(Text), nullable=True)
    metadata = Column(JSONB, nullable=True)
    expiry = Column(DateTime(timezone=True), nullable=False)
    single_use = Column(Boolean, default=False, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        from datetime import datetime

        now = now or datetime.utcnow()
        return self.expiry <= now
