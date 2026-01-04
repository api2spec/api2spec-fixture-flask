"""Tea schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TeaType(str, Enum):
    """Valid tea types."""

    GREEN = "green"
    BLACK = "black"
    OOLONG = "oolong"
    WHITE = "white"
    PUERH = "puerh"
    HERBAL = "herbal"
    ROOIBOS = "rooibos"


class CaffeineLevel(str, Enum):
    """Caffeine content levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Tea(BaseModel):
    """Tea entity."""

    id: str = Field(..., description="Tea UUID")
    name: str = Field(..., min_length=1, max_length=100, description="Tea name")
    type: TeaType = Field(..., description="Tea type")
    origin: str | None = Field(default=None, max_length=100, description="Origin region")
    caffeine_level: CaffeineLevel = Field(..., alias="caffeineLevel", description="Caffeine level")
    steep_temp_celsius: int = Field(
        ..., ge=60, le=100, alias="steepTempCelsius", description="Steeping temperature in Celsius"
    )
    steep_time_seconds: int = Field(
        ..., ge=1, le=600, alias="steepTimeSeconds", description="Steeping time in seconds"
    )
    description: str | None = Field(default=None, max_length=1000, description="Description")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    model_config = {"populate_by_name": True}


class CreateTeaRequest(BaseModel):
    """Request body for creating a tea."""

    name: str = Field(..., min_length=1, max_length=100, description="Tea name")
    type: TeaType = Field(..., description="Tea type")
    origin: str | None = Field(default=None, max_length=100, description="Origin region")
    caffeine_level: CaffeineLevel = Field(
        default=CaffeineLevel.MEDIUM, alias="caffeineLevel", description="Caffeine level"
    )
    steep_temp_celsius: int = Field(
        ..., ge=60, le=100, alias="steepTempCelsius", description="Steeping temperature"
    )
    steep_time_seconds: int = Field(
        ..., ge=1, le=600, alias="steepTimeSeconds", description="Steeping time"
    )
    description: str | None = Field(default=None, max_length=1000, description="Description")

    model_config = {"populate_by_name": True}


class UpdateTeaRequest(BaseModel):
    """Request body for PUT (full replacement)."""

    name: str = Field(..., min_length=1, max_length=100)
    type: TeaType = Field(...)
    origin: str | None = Field(default=None, max_length=100)
    caffeine_level: CaffeineLevel = Field(..., alias="caffeineLevel")
    steep_temp_celsius: int = Field(..., ge=60, le=100, alias="steepTempCelsius")
    steep_time_seconds: int = Field(..., ge=1, le=600, alias="steepTimeSeconds")
    description: str | None = Field(default=None, max_length=1000)

    model_config = {"populate_by_name": True}


class PatchTeaRequest(BaseModel):
    """Request body for PATCH (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: TeaType | None = Field(default=None)
    origin: str | None = Field(default=None, max_length=100)
    caffeine_level: CaffeineLevel | None = Field(default=None, alias="caffeineLevel")
    steep_temp_celsius: int | None = Field(default=None, ge=60, le=100, alias="steepTempCelsius")
    steep_time_seconds: int | None = Field(default=None, ge=1, le=600, alias="steepTimeSeconds")
    description: str | None = Field(default=None, max_length=1000)

    model_config = {"populate_by_name": True}


class TeaQuery(BaseModel):
    """Query parameters for listing teas."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    type: TeaType | None = Field(default=None, description="Filter by tea type")
    caffeine_level: CaffeineLevel | None = Field(
        default=None, alias="caffeineLevel", description="Filter by caffeine level"
    )

    model_config = {"populate_by_name": True}
