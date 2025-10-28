from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from passlib.context import CryptContext
import jwt

from src.core.config import get_settings

# Password hashing context using bcrypt
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return _pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return _pwd_context.hash(password)


# PUBLIC_INTERFACE
def create_access_token(subject: str | int, expires_minutes: Optional[int] = None, extra_claims: Optional[dict[str, Any]] = None) -> str:
    """Create a signed JWT access token.
    Args:
        subject: The subject of the token (typically user id or email).
        expires_minutes: Minutes until expiration. Defaults to config value.
        extra_claims: Optional extra claims to include.
    Returns:
        Encoded JWT as a string.
    """
    settings = get_settings()
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)

    to_encode: dict[str, Any] = {"sub": str(subject), "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return encoded_jwt


# PUBLIC_INTERFACE
def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT, returning its payload if valid; raises jwt exceptions if invalid."""
    settings = get_settings()
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    return payload
