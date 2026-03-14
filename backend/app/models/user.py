from app.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, null
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Nullable for users who sign in only via Google (or other OAuth)
    hashed_password = Column(String, nullable=True)
    # Google OAuth subject id (unique per Google account); set when user signs in with Google
    google_id = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
