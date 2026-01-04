"""Brew schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .tea import Tea
from .teapot import Teapot


class BrewStatus(str, Enum):
    """Brew status values."""

    PREPARING = "preparing"
    STEEPING = "steeping"
    READY = "ready"
    SERVED = "served"
    COLD = "cold"


class Brew(BaseModel):
    """Brew session entity."""

    id: str = Field(..., description="Brew UUID")
    teapot_id: str = Field(..., alias="teapotId", description="Teapot UUID")
    tea_id: str = Field(..., alias="teaId", description="Tea UUID")
    status: BrewStatus = Field(..., description="Brew status")
    water_temp_celsius: int = Field(
        ..., ge=60, le=100, alias="waterTempCelsius", description="Water temperature"
    )
    notes: str | None = Field(default=None, max_length=500, description="Brewing notes")
    started_at: datetime = Field(..., alias="startedAt", description="Start timestamp")
    completed_at: datetime | None = Field(
        default=None, alias="completedAt", description="Completion timestamp"
    )
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    model_config = {"populate_by_name": True}


class BrewWithDetails(Brew):
    """Brew with related teapot and tea."""

    teapot: Teapot = Field(..., description="Related teapot")
    tea: Tea = Field(..., description="Related tea")


class CreateBrewRequest(BaseModel):
    """Request body for creating a brew."""

    teapot_id: str = Field(..., alias="teapotId", description="Teapot UUID")
    tea_id: str = Field(..., alias="teaId", description="Tea UUID")
    water_temp_celsius: int | None = Field(
        default=None, ge=60, le=100, alias="waterTempCelsius", description="Water temperature"
    )
    notes: str | None = Field(default=None, max_length=500, description="Brewing notes")

    model_config = {"populate_by_name": True}


class PatchBrewRequest(BaseModel):
    """Request body for PATCH."""

    status: BrewStatus | None = Field(default=None, description="Brew status")
    notes: str | None = Field(default=None, max_length=500, description="Brewing notes")
    completed_at: datetime | None = Field(
        default=None, alias="completedAt", description="Completion timestamp"
    )

    model_config = {"populate_by_name": True}


class BrewQuery(BaseModel):
    """Query parameters for listing brews."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    status: BrewStatus | None = Field(default=None, description="Filter by status")
    teapot_id: str | None = Field(default=None, alias="teapotId", description="Filter by teapot")
    tea_id: str | None = Field(default=None, alias="teaId", description="Filter by tea")

    model_config = {"populate_by_name": True}
