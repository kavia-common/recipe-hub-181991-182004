from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.core.config import get_settings
from src.db.database import init_db
from src.api.routers import auth as auth_router
from src.api.routers import users as users_router
from src.api.routers import recipes as recipes_router
from src.api.routers import favorites as favorites_router

openapi_tags = [
    {"name": "Health", "description": "Health check endpoint"},
    {"name": "Auth", "description": "Authentication endpoints"},
    {"name": "Users", "description": "User profile and personal data endpoints"},
    {"name": "Recipes", "description": "Recipe discovery and management"},
    {"name": "Favorites", "description": "Favorite recipes management"},
]

app = FastAPI(
    title="Recipe Hub API",
    description="Backend API for recipe management, users, and favorites.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

settings = get_settings()

# Configure CORS using settings; ensure localhost:3000 and preview URL are allowed.
origins = set(settings.CORS_ORIGINS or [])
origins.update({"http://localhost:3000", "http://127.0.0.1:3000"})

# Optionally include preview URL from environment (for ephemeral deployments)
preview_url = os.getenv("PREVIEW_URL")
if preview_url:
    origins.add(preview_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database (development) on app startup."""
    init_db()


# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["Health"])
def health_check():
    """Return a simple health check message."""
    return {"message": "Healthy"}


# Include API routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(recipes_router.router)
app.include_router(favorites_router.router)
