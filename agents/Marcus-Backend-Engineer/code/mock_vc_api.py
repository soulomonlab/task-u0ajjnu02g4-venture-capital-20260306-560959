from fastapi import FastAPI, HTTPException, Depends, Cookie
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="Mock VC Backend API", version="0.1")

# --- Models ---
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    roles: list
    company: Optional[str]

class Venture(BaseModel):
    id: str
    name: str
    short_description: Optional[str]
    stage: str
    sector: str
    logo_url: Optional[str]
    founded_year: Optional[int]

class VenturesList(BaseModel):
    items: list
    next_cursor: Optional[str]

class DocumentItem(BaseModel):
    id: str
    name: str
    type: str
    size: Optional[int]
    uploaded_at: Optional[str]

class UploadUrlRequest(BaseModel):
    venture_id: str
    file_name: str
    content_type: str
    purpose: Optional[str]

class UploadUrlResponse(BaseModel):
    upload_url: str
    method: str
    headers: dict
    expires_in: int

# --- Auth ---
@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    # mock: accept any password
    token = "mocked.jwt.token"
    response = JSONResponse(content={"access_token": token, "token_type": "bearer", "expires_in": 900})
    # set mock refresh cookie
    response.set_cookie(key="refresh_token", value="mock-refresh-token", httponly=True, secure=False, path="/api/v1/auth/refresh", max_age=604800)
    return response

@app.post("/api/v1/auth/refresh", response_model=LoginResponse)
def refresh(refresh_token: Optional[str] = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token cookie")
    token = "mocked.new.jwt.token"
    response = JSONResponse(content={"access_token": token, "token_type": "bearer", "expires_in": 900})
    response.set_cookie(key="refresh_token", value="mock-refresh-token-rotated", httponly=True, secure=False, path="/api/v1/auth/refresh", max_age=604800)
    return response

@app.post("/api/v1/auth/logout")
def logout():
    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")
    return response

# --- User ---
@app.get("/api/v1/users/me", response_model=User)
def me():
    return {"id": str(uuid4()), "email": "user@example.com", "full_name": "Demo User", "roles": ["investor"], "company": "Demo VC"}

# --- Ventures ---
@app.get("/api/v1/ventures", response_model=VenturesList)
def list_ventures(limit: int = 20, cursor: Optional[str] = None):
    items = []
    for i in range(min(limit, 3)):
        items.append({"id": str(uuid4()), "name": f"Startup {i+1}", "short_description": "Mock startup", "stage": "seed", "sector": "enterprise_software", "logo_url": None, "founded_year": 2020})
    return {"items": items, "next_cursor": None}

@app.get("/api/v1/ventures/{venture_id}")
def get_venture(venture_id: str):
    return {"id": venture_id, "name": "Startup A", "description": "Full description", "stage": "seed", "sector": "enterprise_software", "metrics": {"mrr": 10000, "growth_mom": 12.5}, "founders": [{"id": str(uuid4()), "name": "Founder Name"}], "documents": [{"id": str(uuid4()), "name": "Pitch Deck.pdf", "type": "pitch_deck", "uploaded_at": "2024-01-01T12:00:00Z"}]}

# --- Documents ---
@app.get("/api/v1/ventures/{venture_id}/documents", response_model=dict)
def list_documents(venture_id: str):
    items = [{"id": str(uuid4()), "name": "Pitch Deck.pdf", "type": "pitch_deck", "size": 123456}]
    return {"items": items}

@app.post("/api/v1/documents/upload-url", response_model=UploadUrlResponse)
def get_upload_url(req: UploadUrlRequest):
    return {"upload_url": f"https://s3.mock/{str(uuid4())}", "method": "PUT", "headers": {"Content-Type": req.content_type}, "expires_in": 120}

@app.get("/api/v1/documents/{doc_id}/download-url", response_model=dict)
def get_download_url(doc_id: str):
    return {"download_url": f"https://s3.mock/{doc_id}?signature=mock", "expires_in": 300}

@app.post("/api/v1/documents", response_model=DocumentItem, status_code=201)
def create_document(payload: dict):
    return {"id": str(uuid4()), "name": payload.get("file_name"), "type": payload.get("type"), "size": payload.get("size"), "uploaded_at": "2024-01-01T12:00:00Z"}
