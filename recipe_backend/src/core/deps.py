from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.security import decode_token
from src.db.database import get_db
from src.db import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# PUBLIC_INTERFACE
def db_session() -> Generator[Session, None, None]:
    """Provide a DB session dependency."""
    yield from get_db()


# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_session)) -> models.User:
    """Return the current authenticated user by validating the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except Exception:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user


# PUBLIC_INTERFACE
def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Return current user; placeholder for additional 'active' checks."""
    return current_user
