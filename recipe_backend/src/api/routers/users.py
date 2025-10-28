from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.deps import get_current_active_user, db_session
from src.db import models
from src.db.schemas import UserOut, RecipeOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut, summary="Get current user profile")
def read_me(current_user: models.User = Depends(get_current_active_user)) -> UserOut:
    """Return the current authenticated user's profile."""
    return current_user  # Pydantic from_attributes will handle conversion


def _serialize_recipe_with_favorite(recipe: models.Recipe, db: Session, user_id: int) -> RecipeOut:
    """Helper to serialize a recipe including is_favorite field."""
    is_fav = (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == user_id, models.Favorite.recipe_id == recipe.id)
        .first()
        is not None
    )
    # Build tags and ingredients to satisfy RecipeOut models
    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        instructions=recipe.instructions,
        created_at=recipe.created_at,
        owner_id=recipe.owner_id,
        tags=[{"id": rt.id, "tag": {"id": rt.tag.id, "name": rt.tag.name}} for rt in recipe.tags],
        ingredients=[
            {
                "id": ri.id,
                "ingredient": {"id": ri.ingredient.id, "name": ri.ingredient.name},
                "quantity": ri.quantity,
                "unit": ri.unit,
            }
            for ri in recipe.ingredients
        ],
        is_favorite=is_fav,
    )


@router.get("/me/recipes", response_model=List[RecipeOut], summary="List my recipes")
def my_recipes(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(db_session),
) -> list[RecipeOut]:
    """List recipes created by the current user."""
    recipes = db.query(models.Recipe).filter(models.Recipe.owner_id == current_user.id).all()
    return [_serialize_recipe_with_favorite(r, db, current_user.id) for r in recipes]


@router.get("/me/favorites", response_model=List[RecipeOut], summary="List my favorite recipes")
def my_favorites(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(db_session),
) -> list[RecipeOut]:
    """List recipes the current user has favorited."""
    favs = db.query(models.Favorite).filter(models.Favorite.user_id == current_user.id).all()
    recipe_ids = [f.recipe_id for f in favs]
    if not recipe_ids:
        return []
    recipes = db.query(models.Recipe).filter(models.Recipe.id.in_(recipe_ids)).all()
    return [_serialize_recipe_with_favorite(r, db, current_user.id) for r in recipes]
