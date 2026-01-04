# Flask Fixture Specification

**Repository:** `api2spec-fixture-flask`  
**GitHub:** `github.com/api2spec/api2spec-fixture-flask`  
**Purpose:** Target fixture (no native OpenAPI generation)

---

## Quick Reference

| Property | Value |
|----------|-------|
| Language | Python 3.12+ |
| Framework | Flask 3.x |
| Schema Library | Pydantic v2 |
| Package Manager | Poetry |
| Test Runner | pytest |

---

## Project Setup

### Initialize

```bash
mkdir api2spec-fixture-flask
cd api2spec-fixture-flask
poetry init --name api2spec-fixture-flask --python "^3.12"
poetry add flask pydantic uuid6
poetry add --group dev pytest pytest-flask httpx mypy ruff
```

### pyproject.toml

```toml
[tool.poetry]
name = "api2spec-fixture-flask"
version = "1.0.0"
description = "Flask fixture API for api2spec. TIF-compliant."
authors = ["llbbl"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.12"
flask = "^3.0.0"
pydantic = "^2.9.0"
uuid6 = "^2024.7.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-flask = "^1.3.0"
httpx = "^0.27.0"
mypy = "^1.11.0"
ruff = "^0.6.0"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## Directory Structure

```
api2spec-fixture-flask/
├── docs/
│   └── SPEC.md                  # This file
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── __init__.py          # Blueprint registration
│   │   ├── teapots.py           # Teapot routes
│   │   ├── teas.py              # Tea routes
│   │   ├── brews.py             # Brew routes
│   │   └── health.py            # Health + TIF 418
│   ├── schemas/
│   │   ├── __init__.py          # Re-exports
│   │   ├── teapot.py            # Teapot Pydantic models
│   │   ├── tea.py               # Tea Pydantic models
│   │   ├── brew.py              # Brew Pydantic models
│   │   ├── steep.py             # Steep Pydantic models
│   │   └── common.py            # Pagination, Error, etc.
│   └── store/
│       ├── __init__.py
│       └── memory.py            # In-memory data store
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   └── test_teapots.py          # Example tests
├── expected/
│   └── openapi.yaml             # Expected api2spec output
├── api2spec.config.py           # api2spec configuration
├── pyproject.toml
└── README.md
```

---

## Schemas to Implement

### app/schemas/common.py

```python
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
```

### app/schemas/teapot.py

```python
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
```

### app/schemas/tea.py

```python
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
```

### app/schemas/brew.py

```python
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
```

### app/schemas/steep.py

```python
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
```

### app/schemas/__init__.py

```python
"""Schema exports."""

from .brew import (
    Brew,
    BrewQuery,
    BrewStatus,
    BrewWithDetails,
    CreateBrewRequest,
    PatchBrewRequest,
)
from .common import (
    ErrorResponse,
    HealthCheck,
    HealthResponse,
    HealthStatus,
    Pagination,
    PaginatedResponse,
    PaginationQuery,
    TeapotErrorResponse,
)
from .steep import CreateSteepRequest, Steep
from .tea import (
    CaffeineLevel,
    CreateTeaRequest,
    PatchTeaRequest,
    Tea,
    TeaQuery,
    TeaType,
    UpdateTeaRequest,
)
from .teapot import (
    CreateTeapotRequest,
    PatchTeapotRequest,
    Teapot,
    TeapotMaterial,
    TeapotQuery,
    TeapotStyle,
    UpdateTeapotRequest,
)

__all__ = [
    # Common
    "ErrorResponse",
    "HealthCheck",
    "HealthResponse",
    "HealthStatus",
    "Pagination",
    "PaginatedResponse",
    "PaginationQuery",
    "TeapotErrorResponse",
    # Teapot
    "Teapot",
    "TeapotMaterial",
    "TeapotStyle",
    "CreateTeapotRequest",
    "UpdateTeapotRequest",
    "PatchTeapotRequest",
    "TeapotQuery",
    # Tea
    "Tea",
    "TeaType",
    "CaffeineLevel",
    "CreateTeaRequest",
    "UpdateTeaRequest",
    "PatchTeaRequest",
    "TeaQuery",
    # Brew
    "Brew",
    "BrewWithDetails",
    "BrewStatus",
    "CreateBrewRequest",
    "PatchBrewRequest",
    "BrewQuery",
    # Steep
    "Steep",
    "CreateSteepRequest",
]
```

---

## Routes to Implement

### Route Summary Table

| Method | Path | Request Body | Query Params | Success | Errors |
|--------|------|--------------|--------------|---------|--------|
| GET | `/teapots` | — | page, limit, material, style | 200 | — |
| POST | `/teapots` | CreateTeapotRequest | — | 201 | 400 |
| GET | `/teapots/<id>` | — | — | 200 | 404 |
| PUT | `/teapots/<id>` | UpdateTeapotRequest | — | 200 | 400, 404 |
| PATCH | `/teapots/<id>` | PatchTeapotRequest | — | 200 | 400, 404 |
| DELETE | `/teapots/<id>` | — | — | 204 | 404 |
| GET | `/teapots/<teapot_id>/brews` | — | page, limit | 200 | 404 |
| GET | `/teas` | — | page, limit, type, caffeineLevel | 200 | — |
| POST | `/teas` | CreateTeaRequest | — | 201 | 400 |
| GET | `/teas/<id>` | — | — | 200 | 404 |
| PUT | `/teas/<id>` | UpdateTeaRequest | — | 200 | 400, 404 |
| PATCH | `/teas/<id>` | PatchTeaRequest | — | 200 | 400, 404 |
| DELETE | `/teas/<id>` | — | — | 204 | 404 |
| GET | `/brews` | — | page, limit, status, teapotId, teaId | 200 | — |
| POST | `/brews` | CreateBrewRequest | — | 201 | 400 |
| GET | `/brews/<id>` | — | — | 200 | 404 |
| PATCH | `/brews/<id>` | PatchBrewRequest | — | 200 | 400, 404 |
| DELETE | `/brews/<id>` | — | — | 204 | 404 |
| GET | `/brews/<brew_id>/steeps` | — | page, limit | 200 | 404 |
| POST | `/brews/<brew_id>/steeps` | CreateSteepRequest | — | 201 | 400, 404 |
| GET | `/health` | — | — | 200 | — |
| GET | `/health/live` | — | — | 200 | — |
| GET | `/health/ready` | — | — | 200/503 | — |
| GET | `/brew` | — | — | **418** | — |

### app/routes/teapots.py

```python
"""Teapot routes."""

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from app.schemas import (
    CreateTeapotRequest,
    ErrorResponse,
    PatchTeapotRequest,
    Pagination,
    Teapot,
    TeapotQuery,
    UpdateTeapotRequest,
)
from app.store import store

bp = Blueprint("teapots", __name__, url_prefix="/teapots")


@bp.route("", methods=["GET"])
def list_teapots() -> tuple[Response, int]:
    """List all teapots.

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)
        material (str): Filter by material
        style (str): Filter by style

    Returns:
        200: PaginatedResponse[Teapot]
    """
    try:
        query = TeapotQuery(**request.args.to_dict())
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid query parameters",
            details={err["loc"][0]: err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    teapots, total = store.list_teapots(query)
    total_pages = (total + query.limit - 1) // query.limit

    return jsonify({
        "data": [t.model_dump(by_alias=True) for t in teapots],
        "pagination": Pagination(
            page=query.page,
            limit=query.limit,
            total=total,
            total_pages=total_pages,
        ).model_dump(by_alias=True),
    }), 200


@bp.route("", methods=["POST"])
def create_teapot() -> tuple[Response, int]:
    """Create a new teapot.

    Request Body:
        CreateTeapotRequest

    Returns:
        201: Teapot
        400: ErrorResponse
    """
    try:
        data = CreateTeapotRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    now = datetime.now(timezone.utc)
    teapot = Teapot(
        id=str(uuid4()),
        name=data.name,
        material=data.material,
        capacity_ml=data.capacity_ml,
        style=data.style,
        description=data.description,
        created_at=now,
        updated_at=now,
    )

    store.create_teapot(teapot)
    return jsonify(teapot.model_dump(by_alias=True)), 201


@bp.route("/<id>", methods=["GET"])
def get_teapot(id: str) -> tuple[Response, int]:
    """Get a teapot by ID.

    Path Parameters:
        id (str): Teapot UUID

    Returns:
        200: Teapot
        404: ErrorResponse
    """
    teapot = store.get_teapot(id)
    if teapot is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Teapot not found",
        ).model_dump(by_alias=True)), 404

    return jsonify(teapot.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["PUT"])
def update_teapot(id: str) -> tuple[Response, int]:
    """Update a teapot (full replacement).

    Path Parameters:
        id (str): Teapot UUID

    Request Body:
        UpdateTeapotRequest

    Returns:
        200: Teapot
        400: ErrorResponse
        404: ErrorResponse
    """
    existing = store.get_teapot(id)
    if existing is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Teapot not found",
        ).model_dump(by_alias=True)), 404

    try:
        data = UpdateTeapotRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    teapot = Teapot(
        id=id,
        name=data.name,
        material=data.material,
        capacity_ml=data.capacity_ml,
        style=data.style,
        description=data.description,
        created_at=existing.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    store.update_teapot(teapot)
    return jsonify(teapot.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["PATCH"])
def patch_teapot(id: str) -> tuple[Response, int]:
    """Partially update a teapot.

    Path Parameters:
        id (str): Teapot UUID

    Request Body:
        PatchTeapotRequest

    Returns:
        200: Teapot
        400: ErrorResponse
        404: ErrorResponse
    """
    existing = store.get_teapot(id)
    if existing is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Teapot not found",
        ).model_dump(by_alias=True)), 404

    try:
        data = PatchTeapotRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    # Apply patches
    update_data = data.model_dump(exclude_unset=True)
    teapot_data = existing.model_dump()
    teapot_data.update(update_data)
    teapot_data["updated_at"] = datetime.now(timezone.utc)

    teapot = Teapot.model_validate(teapot_data)
    store.update_teapot(teapot)
    return jsonify(teapot.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["DELETE"])
def delete_teapot(id: str) -> tuple[Response | str, int]:
    """Delete a teapot.

    Path Parameters:
        id (str): Teapot UUID

    Returns:
        204: No Content
        404: ErrorResponse
    """
    if not store.delete_teapot(id):
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Teapot not found",
        ).model_dump(by_alias=True)), 404

    return "", 204
```

### app/routes/health.py

```python
"""Health check routes."""

from datetime import datetime, timezone

from flask import Blueprint, Response, jsonify

from app.schemas import HealthCheck, HealthResponse, HealthStatus, TeapotErrorResponse

bp = Blueprint("health", __name__)


@bp.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Basic health check.

    Returns:
        200: HealthResponse
    """
    return jsonify(HealthResponse(
        status=HealthStatus.OK,
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
    ).model_dump(by_alias=True)), 200


@bp.route("/health/live", methods=["GET"])
def live() -> tuple[Response, int]:
    """Liveness probe.

    Returns:
        200: {"status": "ok"}
    """
    return jsonify({"status": "ok"}), 200


@bp.route("/health/ready", methods=["GET"])
def ready() -> tuple[Response, int]:
    """Readiness probe.

    Returns:
        200: HealthResponse (all checks pass)
        503: HealthResponse (some checks fail)
    """
    checks = [
        HealthCheck(name="memory", status=HealthStatus.OK),
        HealthCheck(name="database", status=HealthStatus.OK),
    ]

    all_ok = all(c.status == HealthStatus.OK for c in checks)
    status = HealthStatus.OK if all_ok else HealthStatus.DEGRADED
    status_code = 200 if all_ok else 503

    return jsonify(HealthResponse(
        status=status,
        timestamp=datetime.now(timezone.utc),
        checks=checks,
    ).model_dump(by_alias=True)), status_code


@bp.route("/brew", methods=["GET"])
def brew() -> tuple[Response, int]:
    """TIF 418 signature endpoint.

    Returns:
        418: TeapotErrorResponse
    """
    return jsonify(TeapotErrorResponse(
        error="I'm a teapot",
        message="This server is TIF-compliant and cannot brew coffee",
        spec="https://teapotframework.dev",
    ).model_dump(by_alias=True)), 418
```

### app/routes/__init__.py

```python
"""Route blueprint registration."""

from flask import Flask

from . import brews, health, teapots, teas


def register_routes(app: Flask) -> None:
    """Register all route blueprints."""
    app.register_blueprint(health.bp)
    app.register_blueprint(teapots.bp)
    app.register_blueprint(teas.bp)
    app.register_blueprint(brews.bp)
```

### app/__init__.py

```python
"""Flask application factory."""

from flask import Flask, Response, jsonify

from app.routes import register_routes
from app.schemas import ErrorResponse


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Register routes
    register_routes(app)

    # 404 handler
    @app.errorhandler(404)
    def not_found(e: Exception) -> tuple[Response, int]:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Resource not found",
        ).model_dump(by_alias=True)), 404

    # 500 handler
    @app.errorhandler(500)
    def internal_error(e: Exception) -> tuple[Response, int]:
        return jsonify(ErrorResponse(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred",
        ).model_dump(by_alias=True)), 500

    return app
```

---

## In-Memory Store

### app/store/memory.py

```python
"""In-memory data store."""

from threading import Lock

from app.schemas import (
    Brew,
    BrewQuery,
    Steep,
    Tea,
    TeaQuery,
    Teapot,
    TeapotQuery,
)


class MemoryStore:
    """Thread-safe in-memory data store."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._teapots: dict[str, Teapot] = {}
        self._teas: dict[str, Tea] = {}
        self._brews: dict[str, Brew] = {}
        self._steeps: dict[str, Steep] = {}

    # Teapot methods
    def list_teapots(self, query: TeapotQuery) -> tuple[list[Teapot], int]:
        with self._lock:
            items = list(self._teapots.values())

            # Apply filters
            if query.material:
                items = [t for t in items if t.material == query.material]
            if query.style:
                items = [t for t in items if t.style == query.style]

            total = len(items)
            start = (query.page - 1) * query.limit
            end = start + query.limit

            return items[start:end], total

    def create_teapot(self, teapot: Teapot) -> None:
        with self._lock:
            self._teapots[teapot.id] = teapot

    def get_teapot(self, id: str) -> Teapot | None:
        with self._lock:
            return self._teapots.get(id)

    def update_teapot(self, teapot: Teapot) -> None:
        with self._lock:
            self._teapots[teapot.id] = teapot

    def delete_teapot(self, id: str) -> bool:
        with self._lock:
            if id not in self._teapots:
                return False
            del self._teapots[id]
            return True

    # Similar methods for Tea, Brew, Steep...


# Global store instance
store = MemoryStore()
```

### app/store/__init__.py

```python
"""Store exports."""

from .memory import MemoryStore, store

__all__ = ["MemoryStore", "store"]
```

---

## Entry Point

### run.py

```python
"""Development server entry point."""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"🫖 Tea API running at http://localhost:{port}")
    print(f"   TIF signature: http://localhost:{port}/brew")
    app.run(host="0.0.0.0", port=port, debug=True)
```

---

## api2spec Configuration

### api2spec.config.py

```python
"""api2spec configuration."""

config = {
    "framework": "flask",
    "entry": ["app/routes/**/*.py"],
    "exclude": ["**/*_test.py", "**/conftest.py"],
    "output": {
        "path": "generated/openapi.yaml",
        "format": "yaml",
    },
    "openapi": {
        "info": {
            "title": "Tea Brewing API",
            "version": "1.0.0",
            "description": "Flask fixture API for api2spec. TIF-compliant.",
        },
        "servers": [
            {"url": "http://localhost:3000", "description": "Development"},
        ],
        "tags": [
            {"name": "teapots", "description": "Teapot management"},
            {"name": "teas", "description": "Tea catalog"},
            {"name": "brews", "description": "Brewing sessions"},
            {"name": "health", "description": "Health checks"},
        ],
    },
    "schemas": {
        "include": ["app/schemas/**/*.py"],
        "libraries": ["pydantic"],
    },
    "frameworkOptions": {
        "flask": {
            "blueprintNames": ["bp"],
        },
    },
}
```

---

## Implementation Checklist

### Phase 1: Setup
- [ ] Initialize poetry project
- [ ] Create pyproject.toml with dependencies
- [ ] Create directory structure
- [ ] Run `poetry install`

### Phase 2: Schemas
- [ ] app/schemas/common.py (Pagination, Error, Health, TeapotErrorResponse)
- [ ] app/schemas/teapot.py (all Teapot models)
- [ ] app/schemas/tea.py (all Tea models)
- [ ] app/schemas/brew.py (all Brew models)
- [ ] app/schemas/steep.py (all Steep models)
- [ ] app/schemas/__init__.py (re-exports)

### Phase 3: Store
- [ ] app/store/memory.py (in-memory data store)
- [ ] app/store/__init__.py

### Phase 4: Routes
- [ ] app/routes/teapots.py (GET, POST, GET/<id>, PUT/<id>, PATCH/<id>, DELETE/<id>)
- [ ] app/routes/teas.py (same pattern)
- [ ] app/routes/brews.py (+ nested steeps routes)
- [ ] app/routes/health.py (health, live, ready, brew/418)
- [ ] app/routes/__init__.py (registration)

### Phase 5: App Factory
- [ ] app/__init__.py (create_app factory)
- [ ] run.py (entry point)

### Phase 6: Config & Expected Output
- [ ] api2spec.config.py
- [ ] expected/openapi.yaml
- [ ] README.md

### Phase 7: Validation
- [ ] Run `poetry run python run.py` and test all endpoints
- [ ] Verify 418 response at GET /brew
- [ ] Run api2spec and compare output

---

## Notes for Claude Code

1. **Pydantic is the source of truth** — All request/response shapes come from Pydantic models
2. **Use `model_dump(by_alias=True)`** — Always serialize with camelCase aliases
3. **Use `model_validate()`** — For parsing request bodies, not `**request.json`
4. **Docstrings document the API** — Include Parameters, Request Body, Returns sections
5. **Blueprint pattern** — Each resource gets its own Blueprint with url_prefix
6. **Status codes matter** — 201 for create, 204 for delete, 400/404 for errors
7. **The 418 endpoint is required** — TIF signature at GET /brew
8. **PUT vs PATCH** — PUT has all required fields, PATCH uses `| None` for optional
9. **Use `exclude_unset=True`** — For PATCH to only apply provided fields

---

## Testing the Fixture

```bash
# Start the server
poetry run python run.py

# Test endpoints
curl http://localhost:3000/health
curl http://localhost:3000/brew  # Should return 418

# Create a teapot
curl -X POST http://localhost:3000/teapots \
  -H "Content-Type: application/json" \
  -d '{"name":"My Kyusu","material":"clay","capacityMl":350,"style":"kyusu"}'

# List teapots
curl http://localhost:3000/teapots

# Get teapot by ID
curl http://localhost:3000/teapots/{id}
```
