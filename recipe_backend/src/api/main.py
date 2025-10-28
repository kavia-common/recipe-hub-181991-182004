from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.db.database import init_db

app = FastAPI(
    title="Recipe Hub API",
    description="Backend API for recipe management, users, and favorites.",
    version="0.1.0",
)

settings = get_settings()

# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database (development) on app startup."""
    init_db()


@app.get("/", summary="Health Check", tags=["Health"])
def health_check():
    """Return a simple health check message."""
    return {"message": "Healthy"}
