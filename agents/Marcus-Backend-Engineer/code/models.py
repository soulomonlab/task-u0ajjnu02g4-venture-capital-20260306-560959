from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    LargeBinary,
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class EngagementLink(Base):
    __tablename__ = 'engagement_links'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    token_hash = Column(String(64), nullable=False, unique=True)
    title = Column(String(255), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    max_views = Column(Integer, nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public_snapshot = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)

class DashboardSnapshot(Base):
    __tablename__ = 'dashboard_snapshots'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_link_id = Column(UUID(as_uuid=True), ForeignKey('engagement_links.id'), nullable=False)
    payload = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    size_bytes = Column(Integer, nullable=True)

class EngagementViewAudit(Base):
    __tablename__ = 'engagement_view_audit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    engagement_link_id = Column(UUID(as_uuid=True), nullable=False)
    viewer_ip = Column(INET, nullable=True)
    user_agent = Column(String, nullable=True)
    viewed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    referer = Column(String, nullable=True)
