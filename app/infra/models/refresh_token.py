from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timedelta, timezone
import uuid
from app.core.db.base import BaseModel


class RefreshToken(BaseModel):
    """Store refresh tokens bound to user."""

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)

    @classmethod
    def create_token(cls, user_id: int, lifetime_minutes: int = 60 * 24 * 7) -> dict:
        """Return plain dict for repository create."""
        # 不使用timezone.utc，而是使用不带时区的datetime
        expires = datetime.now() + timedelta(minutes=lifetime_minutes)
        return {
            "user_id": user_id,
            "token": str(uuid.uuid4()),
            "expires_at": expires,
            "revoked": False,
        } 