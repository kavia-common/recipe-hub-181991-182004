from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.deps import get_current_active_user, db_session
from src.db import models

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/{recipe_id}", status_code=status.HTTP_201_CREATED, summary="Favorite a recipe")
def add_favorite(
    recipe_id: int,
    db: Session = Depends(db_session),
    current_user: models.User = Depends(get_current_active_user),
):
    """Mark a recipe as favorite for the current user."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    existing = (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == current_user.id, models.Favorite.recipe_id == recipe_id)
        .first()
    )
    if existing:
        return {"status": "ok"}  # idempotent

    fav = models.Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.add(fav)
    db.commit()
    return {"status": "ok"}


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Unfavorite a recipe")
def remove_favorite(
    recipe_id: int,
    db: Session = Depends(db_session),
    current_user: models.User = Depends(get_current_active_user),
):
    """Remove favorite for the current user and recipe."""
    fav = (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == current_user.id, models.Favorite.recipe_id == recipe_id)
        .first()
    )
    if not fav:
        return None
    db.delete(fav)
    db.commit()
    return None
