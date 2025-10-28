from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- User Schemas ----------

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="Full name of the user")


class UserCreate(UserBase):
    password: str = Field(..., description="Plain text password for signup")


class UserOut(UserBase):
    id: int = Field(..., description="User identifier")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# ---------- Token Schemas ----------

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


# ---------- Tag Schemas ----------

class TagBase(BaseModel):
    name: str = Field(..., description="Tag name")


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    id: int = Field(..., description="Tag identifier")

    class Config:
        from_attributes = True


# ---------- Ingredient Schemas ----------

class IngredientBase(BaseModel):
    name: str = Field(..., description="Ingredient name")


class IngredientCreate(IngredientBase):
    pass


class IngredientOut(IngredientBase):
    id: int = Field(..., description="Ingredient identifier")

    class Config:
        from_attributes = True


# ---------- Recipe Schemas ----------

class RecipeIngredientIn(BaseModel):
    ingredient_id: int = Field(..., description="Ingredient ID")
    quantity: Optional[float] = Field(None, description="Quantity of the ingredient")
    unit: Optional[str] = Field(None, description="Unit for the quantity")


class RecipeIngredientOut(BaseModel):
    id: int = Field(..., description="RecipeIngredient association ID")
    ingredient: IngredientOut = Field(..., description="Ingredient entity")
    quantity: Optional[float] = Field(None, description="Quantity of the ingredient")
    unit: Optional[str] = Field(None, description="Unit for the quantity")

    class Config:
        from_attributes = True


class RecipeTagIn(BaseModel):
    tag_id: int = Field(..., description="Tag ID")


class RecipeTagOut(BaseModel):
    id: int = Field(..., description="RecipeTag association ID")
    tag: TagOut = Field(..., description="Tag entity")

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    instructions: Optional[str] = Field(None, description="Preparation steps")


class RecipeCreate(RecipeBase):
    tags: List[RecipeTagIn] = Field(default_factory=list, description="Tags to associate")
    ingredients: List[RecipeIngredientIn] = Field(default_factory=list, description="Ingredients to associate")


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    instructions: Optional[str] = Field(None, description="Updated instructions")
    tags: Optional[List[RecipeTagIn]] = Field(None, description="Replace all tags")
    ingredients: Optional[List[RecipeIngredientIn]] = Field(None, description="Replace all ingredients")


class RecipeOut(BaseModel):
    id: int = Field(..., description="Recipe ID")
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    instructions: Optional[str] = Field(None, description="Preparation steps")
    created_at: datetime = Field(..., description="Creation timestamp")
    owner_id: int = Field(..., description="Owner user ID")

    tags: List[RecipeTagOut] = Field(default_factory=list, description="Associated tags")
    ingredients: List[RecipeIngredientOut] = Field(default_factory=list, description="Associated ingredients")
    is_favorite: bool = Field(False, description="Whether current user has favorited this recipe")

    class Config:
        from_attributes = True


# ---------- Pagination (optional) ----------

class Pagination(BaseModel):
    total: int = Field(..., description="Total items")
    page: int = Field(..., description="Current page number (1-based)")
    size: int = Field(..., description="Page size")
