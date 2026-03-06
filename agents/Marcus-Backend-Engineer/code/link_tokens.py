"""
FastAPI router stubs for link token lifecycle and upload presign endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime

from ..services.link_token_service import create_link_token, verify_link_token, consume_link_token
from ..models.link_token import LinkToken
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/api/v1/link-tokens", tags=["link-tokens"])


class CreateLinkRequest(BaseModel):
    allowed_emails: list[EmailStr] | None = None
    ttl_seconds: int = 3600
    single_use: bool = False
    metadata: dict | None = None


class CreateLinkResponse(BaseModel):
    token: str
    id: str
    expiry: datetime


@router.post("/", response_model=CreateLinkResponse)
def create_link(req: CreateLinkRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Authorization: only owners with appropriate role can create
    raw_token, lt = create_link_token(
        db=db,
        owner_id=user.id,
        allowed_emails=req.allowed_emails,
        ttl_seconds=req.ttl_seconds,
        single_use=req.single_use,
        metadata=req.metadata,
    )
    return CreateLinkResponse(token=raw_token, id=str(lt.id), expiry=lt.expiry)


class ValidateResponse(BaseModel):
    valid: bool
    id: str | None = None
    expiry: datetime | None = None
    single_use: bool | None = None
    allowed_emails: list[EmailStr] | None = None


@router.post("/validate", response_model=ValidateResponse)
def validate_link(token: str, db: Session = Depends(get_db)):
    lt = verify_link_token(db, token)
    if not lt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    # Do not consume here; caller may call consume endpoint if performing single-use
    return ValidateResponse(
        valid=True,
        id=str(lt.id),
        expiry=lt.expiry,
        single_use=lt.single_use,
        allowed_emails=lt.allowed_emails,
    )


class ConsumeRequest(BaseModel):
    token: str


@router.post("/consume")
def consume(req: ConsumeRequest, db: Session = Depends(get_db)):
    lt = verify_link_token(db, req.token)
    if not lt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    success = consume_link_token(db, lt)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to consume token")
    return {"ok": True}


# Placeholder for presign upload endpoint: requires virus-scan pipeline integration
class PresignRequest(BaseModel):
    filename: str
    content_type: str
    size_bytes: int


class PresignResponse(BaseModel):
    url: str
    fields: dict | None = None
    ttl_seconds: int


@router.post("/presign", response_model=PresignResponse)
def presign_upload(req: PresignRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # TODO: enforce max size, content-type allowlist, quota, and attach scanning job after upload
    # For now return a stub short-lived URL (frontend should not use until integration complete)
    # In prod: generate S3 presigned POST or PUT with short TTL and server-side encryption
    presigned_url = "https://s3.example.com/presigned-upload-url"
    return PresignResponse(url=presigned_url, fields=None, ttl_seconds=300)
