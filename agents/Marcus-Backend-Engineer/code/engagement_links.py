from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import hashlib, base64, os
from sqlalchemy.orm import Session

from models import EngagementLink, DashboardSnapshot, EngagementViewAudit
from database import get_db

router = APIRouter()

class CreateLinkRequest(BaseModel):
    title: Optional[str]
    expires_in_seconds: Optional[int] = Field(None, ge=60)
    max_views: Optional[int]
    is_public_snapshot: Optional[bool] = True
    metadata: Optional[dict]

class CreateLinkResponse(BaseModel):
    id: str
    token: str

@router.post('/engagement-links', response_model=CreateLinkResponse)
async def create_link(req: CreateLinkRequest, db: Session = Depends(get_db), request: Request = None):
    # For brevity, auth check placeholder
    creator_id = request.headers.get('X-User-Id')
    if not creator_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    raw_token = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    expires_at = None
    if req.expires_in_seconds:
        expires_at = datetime.utcnow() + timedelta(seconds=req.expires_in_seconds)

    link = EngagementLink(
        creator_id=creator_id,
        token_hash=token_hash,
        title=req.title,
        expires_at=expires_at,
        max_views=req.max_views,
        is_public_snapshot=req.is_public_snapshot,
        metadata=req.metadata,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    return CreateLinkResponse(id=str(link.id), token=raw_token)

@router.post('/engagement-links/{id}/revoke')
async def revoke_link(id: str = Path(...), db: Session = Depends(get_db), request: Request = None):
    creator_id = request.headers.get('X-User-Id')
    if not creator_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    link = db.query(EngagementLink).filter(EngagementLink.id == id, EngagementLink.creator_id == creator_id).first()
    if not link:
        raise HTTPException(status_code=404, detail='Not found')
    link.revoked_at = datetime.utcnow()
    db.add(link)
    db.commit()
    return {'status': 'revoked'}

@router.get('/share/{token}')
async def share(token: str, request: Request, db: Session = Depends(get_db)):
    # hash token and find link
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    link = db.query(EngagementLink).filter(EngagementLink.token_hash == token_hash).first()
    if not link:
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    if link.revoked_at is not None:
        raise HTTPException(status_code=401, detail='Revoked token')
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail='Expired token')

    # Record audit
    ip = request.client.host if request.client else None
    ua = request.headers.get('user-agent')
    audit = EngagementViewAudit(engagement_link_id=link.id, viewer_ip=ip, user_agent=ua)
    db.add(audit)
    db.commit()

    # Return snapshot if exists
    snapshot = db.query(DashboardSnapshot).filter(DashboardSnapshot.engagement_link_id == link.id).order_by(DashboardSnapshot.generated_at.desc()).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail='Snapshot not available')
    return {'snapshot': snapshot.payload}
