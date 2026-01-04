"""Brew routes."""

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from app.schemas import (
    Brew,
    BrewQuery,
    BrewStatus,
    CreateBrewRequest,
    CreateSteepRequest,
    ErrorResponse,
    Pagination,
    PatchBrewRequest,
    Steep,
)
from app.schemas.common import PaginationQuery
from app.store import store

bp = Blueprint("brews", __name__, url_prefix="/brews")


@bp.route("", methods=["GET"])
def list_brews() -> tuple[Response, int]:
    """List all brews.

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)
        status (str): Filter by status
        teapotId (str): Filter by teapot
        teaId (str): Filter by tea

    Returns:
        200: PaginatedResponse[Brew]
    """
    try:
        query = BrewQuery(**request.args.to_dict())
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid query parameters",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    brews, total = store.list_brews(query)
    total_pages = (total + query.limit - 1) // query.limit if total > 0 else 0

    return jsonify({
        "data": [b.model_dump(by_alias=True) for b in brews],
        "pagination": Pagination(
            page=query.page,
            limit=query.limit,
            total=total,
            total_pages=total_pages,
        ).model_dump(by_alias=True),
    }), 200


@bp.route("", methods=["POST"])
def create_brew() -> tuple[Response, int]:
    """Create a new brew.

    Request Body:
        CreateBrewRequest

    Returns:
        201: Brew
        400: ErrorResponse
    """
    try:
        data = CreateBrewRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    # Validate teapot exists
    teapot = store.get_teapot(data.teapot_id)
    if teapot is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Teapot not found",
        ).model_dump(by_alias=True)), 400

    # Validate tea exists
    tea = store.get_tea(data.tea_id)
    if tea is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Tea not found",
        ).model_dump(by_alias=True)), 400

    now = datetime.now(timezone.utc)
    # Use tea's steep temp if not provided
    water_temp = data.water_temp_celsius if data.water_temp_celsius else tea.steep_temp_celsius

    brew = Brew(
        id=str(uuid4()),
        teapot_id=data.teapot_id,
        tea_id=data.tea_id,
        status=BrewStatus.PREPARING,
        water_temp_celsius=water_temp,
        notes=data.notes,
        started_at=now,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )

    store.create_brew(brew)
    return jsonify(brew.model_dump(by_alias=True)), 201


@bp.route("/<id>", methods=["GET"])
def get_brew(id: str) -> tuple[Response, int]:
    """Get a brew by ID.

    Path Parameters:
        id (str): Brew UUID

    Returns:
        200: Brew
        404: ErrorResponse
    """
    brew = store.get_brew(id)
    if brew is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Brew not found",
        ).model_dump(by_alias=True)), 404

    return jsonify(brew.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["PATCH"])
def patch_brew(id: str) -> tuple[Response, int]:
    """Partially update a brew.

    Path Parameters:
        id (str): Brew UUID

    Request Body:
        PatchBrewRequest

    Returns:
        200: Brew
        400: ErrorResponse
        404: ErrorResponse
    """
    existing = store.get_brew(id)
    if existing is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Brew not found",
        ).model_dump(by_alias=True)), 404

    try:
        data = PatchBrewRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    # Apply patches
    update_data = data.model_dump(exclude_unset=True)
    brew_data = existing.model_dump()
    brew_data.update(update_data)
    brew_data["updated_at"] = datetime.now(timezone.utc)

    brew = Brew.model_validate(brew_data)
    store.update_brew(brew)
    return jsonify(brew.model_dump(by_alias=True)), 200


@bp.route("/<id>", methods=["DELETE"])
def delete_brew(id: str) -> tuple[Response | str, int]:
    """Delete a brew.

    Path Parameters:
        id (str): Brew UUID

    Returns:
        204: No Content
        404: ErrorResponse
    """
    if not store.delete_brew(id):
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Brew not found",
        ).model_dump(by_alias=True)), 404

    return "", 204


@bp.route("/<brew_id>/steeps", methods=["GET"])
def list_steeps(brew_id: str) -> tuple[Response, int]:
    """List steeps for a specific brew.

    Path Parameters:
        brew_id (str): Brew UUID

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)

    Returns:
        200: PaginatedResponse[Steep]
        404: ErrorResponse
    """
    # Check if brew exists
    brew = store.get_brew(brew_id)
    if brew is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Brew not found",
        ).model_dump(by_alias=True)), 404

    try:
        query = PaginationQuery(**request.args.to_dict())
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid query parameters",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    steeps, total = store.list_steeps_by_brew(brew_id, query)
    total_pages = (total + query.limit - 1) // query.limit if total > 0 else 0

    return jsonify({
        "data": [s.model_dump(by_alias=True) for s in steeps],
        "pagination": Pagination(
            page=query.page,
            limit=query.limit,
            total=total,
            total_pages=total_pages,
        ).model_dump(by_alias=True),
    }), 200


@bp.route("/<brew_id>/steeps", methods=["POST"])
def create_steep(brew_id: str) -> tuple[Response, int]:
    """Create a new steep for a brew.

    Path Parameters:
        brew_id (str): Brew UUID

    Request Body:
        CreateSteepRequest

    Returns:
        201: Steep
        400: ErrorResponse
        404: ErrorResponse
    """
    # Check if brew exists
    brew = store.get_brew(brew_id)
    if brew is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Brew not found",
        ).model_dump(by_alias=True)), 404

    try:
        data = CreateSteepRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid request body",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    now = datetime.now(timezone.utc)
    steep_number = store.get_next_steep_number(brew_id)

    steep = Steep(
        id=str(uuid4()),
        brew_id=brew_id,
        steep_number=steep_number,
        duration_seconds=data.duration_seconds,
        rating=data.rating,
        notes=data.notes,
        created_at=now,
    )

    store.create_steep(steep)
    return jsonify(steep.model_dump(by_alias=True)), 201
