"""Tea routes."""

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from app.schemas import (
    CreateTeaRequest,
    ErrorResponse,
    Pagination,
    PatchTeaRequest,
    Tea,
    TeaQuery,
    UpdateTeaRequest,
)
from app.store import store

bp = Blueprint("teas", __name__, url_prefix="/teas")


@bp.route("", methods=["GET"])
def list_teas() -> tuple[Response, int]:
    """List all teas.

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)
        type (str): Filter by tea type
        caffeineLevel (str): Filter by caffeine level

    Returns:
        200: PaginatedResponse[Tea]
    """
    try:
        query = TeaQuery(**request.args.to_dict())
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid query parameters",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    teas, total = store.list_teas(query)
    total_pages = (total + query.limit - 1) // query.limit if total > 0 else 0

    return jsonify({
        "data": [t.model_dump(by_alias=True) for t in teas],
        "pagination": Pagination(
            page=query.page,
            limit=query.limit,
            total=total,
            total_pages=total_pages,
        ).model_dump(by_alias=True),
    }), 200


@bp.route("", methods=["POST"])
def create_tea() -> tuple[Response, int]:
    """Create a new tea.

    Request Body:
        CreateTeaRequest

    Returns:
        201: Tea
        400: ErrorResponse
    """
    try:
        data = CreateTeaRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    now = datetime.now(timezone.utc)
    tea = Tea(
        id=str(uuid4()),
        name=data.name,
        type=data.type,
        origin=data.origin,
        caffeine_level=data.caffeine_level,
        steep_temp_celsius=data.steep_temp_celsius,
        steep_time_seconds=data.steep_time_seconds,
        description=data.description,
        created_at=now,
        updated_at=now,
    )

    store.create_tea(tea)
    return jsonify(tea.model_dump(by_alias=True)), 201


@bp.route("/<id>", methods=["GET"])
def get_tea(id: str) -> tuple[Response, int]:
    """Get a tea by ID.

    Path Parameters:
        id (str): Tea UUID

    Returns:
        200: Tea
        404: ErrorResponse
    """
    tea = store.get_tea(id)
    if tea is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Tea not found",
        ).model_dump(by_alias=True)), 404

    return jsonify(tea.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["PUT"])
def update_tea(id: str) -> tuple[Response, int]:
    """Update a tea (full replacement).

    Path Parameters:
        id (str): Tea UUID

    Request Body:
        UpdateTeaRequest

    Returns:
        200: Tea
        400: ErrorResponse
        404: ErrorResponse
    """
    existing = store.get_tea(id)
    if existing is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Tea not found",
        ).model_dump(by_alias=True)), 404

    try:
        data = UpdateTeaRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    tea = Tea(
        id=id,
        name=data.name,
        type=data.type,
        origin=data.origin,
        caffeine_level=data.caffeine_level,
        steep_temp_celsius=data.steep_temp_celsius,
        steep_time_seconds=data.steep_time_seconds,
        description=data.description,
        created_at=existing.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    store.update_tea(tea)
    return jsonify(tea.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["PATCH"])
def patch_tea(id: str) -> tuple[Response, int]:
    """Partially update a tea.

    Path Parameters:
        id (str): Tea UUID

    Request Body:
        PatchTeaRequest

    Returns:
        200: Tea
        400: ErrorResponse
        404: ErrorResponse
    """
    existing = store.get_tea(id)
    if existing is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Tea not found",
        ).model_dump(by_alias=True)), 404

    try:
        data = PatchTeaRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    # Apply patches
    update_data = data.model_dump(exclude_unset=True)
    tea_data = existing.model_dump()
    tea_data.update(update_data)
    tea_data["updated_at"] = datetime.now(timezone.utc)

    tea = Tea.model_validate(tea_data)
    store.update_tea(tea)
    return jsonify(tea.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["DELETE"])
def delete_tea(id: str) -> tuple[Response | str, int]:
    """Delete a tea.

    Path Parameters:
        id (str): Tea UUID

    Returns:
        204: No Content
        404: ErrorResponse
    """
    if not store.delete_tea(id):
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Tea not found",
        ).model_dump(by_alias=True)), 404

    return "", 204
