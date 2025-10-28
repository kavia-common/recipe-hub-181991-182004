from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.deps import get_current_active_user, db_session
from src.db import models
from src.db.schemas import RecipeCreate, RecipeUpdate, RecipeOut

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _serialize_recipe(recipe: models.Recipe, db: Session, user_id: Optional[int]) -> RecipeOut:
    """Serialize a recipe including is_favorite for the given user."""
    is_fav = False
    if user_id is not None:
        is_fav = (
            db.query(models.Favorite)
            .filter(models.Favorite.user_id == user_id, models.Favorite.recipe_id == recipe.id)
            .first()
            is not None
        )
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


@router.get("", response_model=List[RecipeOut], summary="Search or list recipes")
def list_recipes(
    q: Optional[str] = Query(None, description="Query by title/description"),
    tags: Optional[List[int]] = Query(None, description="Filter by tag ids"),
    ingredients: Optional[List[int]] = Query(None, description="Filter by ingredient ids"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(db_session),
    current_user: models.User | None = Depends(lambda: None),  # optional auth
) -> list[RecipeOut]:
    """List recipes with optional search by query, tags, ingredients, and pagination."""
    query = db.query(models.Recipe)
    if q:
        query = query.filter((models.Recipe.title.ilike(f"%{q}%")) | (models.Recipe.description.ilike(f"%{q}%")))
    if tags:
        query = query.join(models.RecipeTag).filter(models.RecipeTag.tag_id.in_(tags))
    if ingredients:
        query = query.join(models.RecipeIngredient).filter(models.RecipeIngredient.ingredient_id.in_(ingredients))

    offset = (page - 1) * size
    recipes = query.offset(offset).limit(size).all()

    user_id = current_user.id if current_user else None
    return [_serialize_recipe(r, db, user_id) for r in recipes]


@router.post("", response_model=RecipeOut, summary="Create a recipe", status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_in: RecipeCreate,
    db: Session = Depends(db_session),
    current_user: models.User = Depends(get_current_active_user),
) -> RecipeOut:
    """Create a new recipe owned by the current user, with tags and ingredients associations."""
    recipe = models.Recipe(
        title=recipe_in.title,
        description=recipe_in.description,
        instructions=recipe_in.instructions,
        owner_id=current_user.id,
    )
    db.add(recipe)
    db.flush()

    # Tags
    for t in recipe_in.tags or []:
        tag = db.query(models.Tag).filter(models.Tag.id == t.tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag {t.tag_id} not found")
        db.add(models.RecipeTag(recipe_id=recipe.id, tag_id=tag.id))

    # Ingredients
    for ing in recipe_in.ingredients or []:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ing.ingredient_id).first()
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient {ing.ingredient_id} not found")
        db.add(
            models.RecipeIngredient(
                recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=ing.quantity, unit=ing.unit
            )
        )

    db.commit()
    db.refresh(recipe)
    return _serialize_recipe(recipe, db, current_user.id)


def _assert_owner(recipe: models.Recipe, user_id: int):
    if recipe.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this recipe")


@router.get("/{recipe_id}", response_model=RecipeOut, summary="Get a recipe by ID")
def get_recipe(
    recipe_id: int,
    db: Session = Depends(db_session),
    current_user: models.User | None = Depends(lambda: None),
) -> RecipeOut:
    """Retrieve a recipe by id, including tags/ingredients and is_favorite."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    user_id = current_user.id if current_user else None
    return _serialize_recipe(recipe, db, user_id)


@router.put("/{recipe_id}", response_model=RecipeOut, summary="Replace a recipe")
@router.patch("/{recipe_id}", response_model=RecipeOut, summary="Update a recipe")
def update_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    db: Session = Depends(db_session),
    current_user: models.User = Depends(get_current_active_user),
) -> RecipeOut:
    """Update an existing recipe; requires ownership. If tags/ingredients provided, replace them."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    _assert_owner(recipe, current_user.id)

    if recipe_in.title is not None:
        recipe.title = recipe_in.title
    if recipe_in.description is not None:
        recipe.description = recipe_in.description
    if recipe_in.instructions is not None:
        recipe.instructions = recipe_in.instructions

    # Replace associations if provided
    if recipe_in.tags is not None:
        # delete existing
        db.query(models.RecipeTag).filter(models.RecipeTag.recipe_id == recipe.id).delete()
        # add new
        for t in recipe_in.tags:
            tag = db.query(models.Tag).filter(models.Tag.id == t.tag_id).first()
            if not tag:
                raise HTTPException(status_code=404, detail=f"Tag {t.tag_id} not found")
            db.add(models.RecipeTag(recipe_id=recipe.id, tag_id=tag.id))

    if recipe_in.ingredients is not None:
        db.query(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == recipe.id).delete()
        for ing in recipe_in.ingredients:
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ing.ingredient_id).first()
            if not ingredient:
                raise HTTPException(status_code=404, detail=f"Ingredient {ing.ingredient_id} not found")
            db.add(
                models.RecipeIngredient(
                    recipe_id=recipe.id, ingredient_id=ingredient.id, quantity=ing.quantity, unit=ing.unit
                )
            )

    db.commit()
    db.refresh(recipe)
    return _serialize_recipe(recipe, db, current_user.id)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a recipe")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(db_session),
    current_user: models.User = Depends(get_current_active_user),
) -> None:
    """Delete a recipe; requires ownership."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    _assert_owner(recipe, current_user.id)
    db.delete(recipe)
    db.commit()
    return None
