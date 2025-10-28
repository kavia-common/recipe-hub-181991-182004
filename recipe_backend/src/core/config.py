import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables with defaults."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_DEV_SECRET")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    CORS_ORIGINS: List[str] = (
        os.getenv("CORS_ORIGINS", "http://localhost:3000")
        .split(",")
        if os.getenv("CORS_ORIGINS")
        else ["http://localhost:3000"]
    )

    class Config:
        arbitrary_types_allowed = True


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return a singleton Settings instance for app-wide configuration."""
    # In a simple setup, we can instantiate once and reuse.
    # For more complex scenarios, consider lru_cache.
    return Settings()
