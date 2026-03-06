from datetime import datetime
import os
from cryptography.fernet import Fernet
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

def _get_fernet():
    # In production, replace with KMS/Vault retrieval. Here we read from env for demo.
    key = os.getenv("FERNET_KEY")
    if not key:
        # Generate a warning key for local/dev only. DO NOT use in prod.
        key = Fernet.generate_key()
    return Fernet(key)

class Venture(Base):
    __tablename__ = "ventures"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    public_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    interests = relationship("Interest", back_populates="venture")

class Interest(Base):
    __tablename__ = "venture_interests"
    id = Column(Integer, primary_key=True)
    venture_id = Column(Integer, ForeignKey("ventures.id"), nullable=False)
    # Contact details MUST be stored encrypted at rest.
    contact_encrypted = Column(String, nullable=True)
    contact_type = Column(String(50), nullable=True)  # e.g., 'email'
    consent_given = Column(Boolean, default=False)
    preference = Column(String(50), nullable=False, default="curation_queue")
    created_at = Column(DateTime, default=datetime.utcnow)

    venture = relationship("Venture", back_populates="interests")

    def set_contact(self, plaintext: str):
        """Encrypt and store contact info. Use KMS/Vault in prod."""
        f = _get_fernet()
        token = f.encrypt(plaintext.encode("utf-8"))
        # store as text (base64)
        self.contact_encrypted = token.decode("utf-8")
        self.contact_type = "email"

    def get_contact(self) -> str:
        """Decrypt contact info. Access must be audited and restricted."""
        if not self.contact_encrypted:
            return None
        f = _get_fernet()
        try:
            pt = f.decrypt(self.contact_encrypted.encode("utf-8"))
            return pt.decode("utf-8")
        except Exception:
            return None
