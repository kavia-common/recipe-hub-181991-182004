from typing import List

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.db.database import SessionLocal, init_db
from src.db import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def seed():
    """Seed sample users, tags, ingredients, and a couple of recipes."""
    init_db()
    db: Session = SessionLocal()

    try:
        # Users
        if not db.query(models.User).filter(models.User.email == "demo@example.com").first():
            demo = models.User(
                email="demo@example.com",
                hashed_password=_get_password_hash("password"),
                full_name="Demo User",
            )
            db.add(demo)
            db.flush()
        else:
            demo = db.query(models.User).filter(models.User.email == "demo@example.com").first()

        # Tags
        tag_names: List[str] = ["Vegan", "Dessert", "Quick", "Breakfast"]
        tags = {}
        for name in tag_names:
            tag = db.query(models.Tag).filter(models.Tag.name == name).first()
            if not tag:
                tag = models.Tag(name=name)
                db.add(tag)
                db.flush()
            tags[name] = tag

        # Ingredients
        ingredient_names = ["Flour", "Sugar", "Salt", "Milk", "Eggs", "Butter"]
        ingredients = {}
        for name in ingredient_names:
            ing = db.query(models.Ingredient).filter(models.Ingredient.name == name).first()
            if not ing:
                ing = models.Ingredient(name=name)
                db.add(ing)
                db.flush()
            ingredients[name] = ing

        # Recipes
        if not db.query(models.Recipe).filter(models.Recipe.title == "Pancakes").first():
            r = models.Recipe(
                title="Pancakes",
                description="Fluffy pancakes",
                instructions="Mix ingredients and cook on a griddle.",
                owner_id=demo.id,
            )
            db.add(r)
            db.flush()

            # tags
            db.add(models.RecipeTag(recipe_id=r.id, tag_id=tags["Breakfast"].id))
            db.add(models.RecipeTag(recipe_id=r.id, tag_id=tags["Quick"].id))

            # ingredients
            db.add(models.RecipeIngredient(recipe_id=r.id, ingredient_id=ingredients["Flour"].id, quantity=2, unit="cups"))
            db.add(models.RecipeIngredient(recipe_id=r.id, ingredient_id=ingredients["Milk"].id, quantity=1.5, unit="cups"))
            db.add(models.RecipeIngredient(recipe_id=r.id, ingredient_id=ingredients["Eggs"].id, quantity=2, unit="pcs"))
            db.add(models.RecipeIngredient(recipe_id=r.id, ingredient_id=ingredients["Butter"].id, quantity=2, unit="tbsp"))

        if not db.query(models.Recipe).filter(models.Recipe.title == "Vegan Brownies").first():
            r2 = models.Recipe(
                title="Vegan Brownies",
                description="Rich vegan brownies",
                instructions="Combine ingredients and bake.",
                owner_id=demo.id,
            )
            db.add(r2)
            db.flush()

            db.add(models.RecipeTag(recipe_id=r2.id, tag_id=tags["Vegan"].id))
            db.add(models.RecipeTag(recipe_id=r2.id, tag_id=tags["Dessert"].id))

            db.add(models.RecipeIngredient(recipe_id=r2.id, ingredient_id=ingredients["Flour"].id, quantity=1.5, unit="cups"))
            db.add(models.RecipeIngredient(recipe_id=r2.id, ingredient_id=ingredients["Sugar"].id, quantity=1, unit="cup"))
            db.add(models.RecipeIngredient(recipe_id=r2.id, ingredient_id=ingredients["Salt"].id, quantity=0.5, unit="tsp"))

        db.commit()
        print("Seeding complete.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
