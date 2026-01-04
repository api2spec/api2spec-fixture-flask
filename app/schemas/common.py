"""Common schemas used across the API."""

from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


class PaginationQuery(BaseModel):
    """Pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class Pagination(BaseModel):
    """Pagination metadata in responses."""

    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, alias="totalPages", description="Total pages")

    model_config = {"populate_by_name": True}


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    data: list[T]
    pagination: Pagination


class ErrorResponse(BaseModel):
    """API error response."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: dict[str, str] | None = Field(default=None, description="Field-level errors")


class HealthStatus(str, Enum):
    """Health check status values."""

    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"


class HealthCheck(BaseModel):
    """Single health check result."""

    name: str = Field(..., description="Check name")
    status: HealthStatus = Field(..., description="Check status")
    latency_ms: int | None = Field(default=None, alias="latencyMs", description="Latency in ms")
    message: str | None = Field(default=None, description="Optional message")

    model_config = {"populate_by_name": True}


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: HealthStatus = Field(..., description="Overall status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str | None = Field(default=None, description="API version")
    checks: list[HealthCheck] | None = Field(default=None, description="Individual checks")


class TeapotErrorResponse(BaseModel):
    """TIF 418 I'm a teapot response."""

    error: str = Field(default="I'm a teapot", description="Error message")
    message: str = Field(..., description="TIF compliance message")
    spec: str = Field(..., description="TIF specification URL")
