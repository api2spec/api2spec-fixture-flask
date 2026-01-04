"""Teapot schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TeapotMaterial(str, Enum):
    """Valid teapot materials."""

    CERAMIC = "ceramic"
    CAST_IRON = "cast-iron"
    GLASS = "glass"
    PORCELAIN = "porcelain"
    CLAY = "clay"
    STAINLESS_STEEL = "stainless-steel"


class TeapotStyle(str, Enum):
    """Valid teapot styles."""

    KYUSU = "kyusu"
    GAIWAN = "gaiwan"
    ENGLISH = "english"
    MOROCCAN = "moroccan"
    TURKISH = "turkish"
    YIXING = "yixing"


class Teapot(BaseModel):
    """Teapot entity."""

    id: str = Field(..., description="Teapot UUID")
    name: str = Field(..., min_length=1, max_length=100, description="Teapot name")
    material: TeapotMaterial = Field(..., description="Teapot material")
    capacity_ml: int = Field(
        ..., ge=1, le=5000, alias="capacityMl", description="Capacity in milliliters"
    )
    style: TeapotStyle = Field(..., description="Teapot style")
    description: str | None = Field(default=None, max_length=500, description="Description")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    model_config = {"populate_by_name": True}


class CreateTeapotRequest(BaseModel):
    """Request body for creating a teapot."""

    name: str = Field(..., min_length=1, max_length=100, description="Teapot name")
    material: TeapotMaterial = Field(..., description="Teapot material")
    capacity_ml: int = Field(
        ..., ge=1, le=5000, alias="capacityMl", description="Capacity in milliliters"
    )
    style: TeapotStyle = Field(default=TeapotStyle.ENGLISH, description="Teapot style")
    description: str | None = Field(default=None, max_length=500, description="Description")

    model_config = {"populate_by_name": True}


class UpdateTeapotRequest(BaseModel):
    """Request body for PUT (full replacement)."""

    name: str = Field(..., min_length=1, max_length=100, description="Teapot name")
    material: TeapotMaterial = Field(..., description="Teapot material")
    capacity_ml: int = Field(
        ..., ge=1, le=5000, alias="capacityMl", description="Capacity in milliliters"
    )
    style: TeapotStyle = Field(..., description="Teapot style")
    description: str | None = Field(default=None, max_length=500, description="Description")

    model_config = {"populate_by_name": True}


class PatchTeapotRequest(BaseModel):
    """Request body for PATCH (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=100, description="Teapot name")
    material: TeapotMaterial | None = Field(default=None, description="Teapot material")
    capacity_ml: int | None = Field(
        default=None, ge=1, le=5000, alias="capacityMl", description="Capacity in milliliters"
    )
    style: TeapotStyle | None = Field(default=None, description="Teapot style")
    description: str | None = Field(default=None, max_length=500, description="Description")

    model_config = {"populate_by_name": True}


class TeapotQuery(BaseModel):
    """Query parameters for listing teapots."""

    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    material: TeapotMaterial | None = Field(default=None, description="Filter by material")
    style: TeapotStyle | None = Field(default=None, description="Filter by style")
