"""Steep schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class Steep(BaseModel):
    """Steep cycle entity."""

    id: str = Field(..., description="Steep UUID")
    brew_id: str = Field(..., alias="brewId", description="Parent brew UUID")
    steep_number: int = Field(..., ge=1, alias="steepNumber", description="Steep number (1st, 2nd)")
    duration_seconds: int = Field(
        ..., ge=1, alias="durationSeconds", description="Steep duration in seconds"
    )
    rating: int | None = Field(default=None, ge=1, le=5, description="Rating 1-5")
    notes: str | None = Field(default=None, max_length=200, description="Tasting notes")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")

    model_config = {"populate_by_name": True}


class CreateSteepRequest(BaseModel):
    """Request body for creating a steep."""

    duration_seconds: int = Field(
        ..., ge=1, alias="durationSeconds", description="Steep duration in seconds"
    )
    rating: int | None = Field(default=None, ge=1, le=5, description="Rating 1-5")
    notes: str | None = Field(default=None, max_length=200, description="Tasting notes")

    model_config = {"populate_by_name": True}
