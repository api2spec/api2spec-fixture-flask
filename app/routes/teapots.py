"""Teapot routes."""

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from app.schemas import (
    CreateTeapotRequest,
    ErrorResponse,
    Pagination,
    PatchTeapotRequest,
    Teapot,
    TeapotQuery,
    UpdateTeapotRequest,
)
from app.schemas.common import PaginationQuery
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
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    teapots, total = store.list_teapots(query)
    total_pages = (total + query.limit - 1) // query.limit if total > 0 else 0

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


@bp.route("/<teapot_id>/brews", methods=["GET"])
def list_teapot_brews(teapot_id: str) -> tuple[Response, int]:
    """List brews for a specific teapot.

    Path Parameters:
        teapot_id (str): Teapot UUID

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)

    Returns:
        200: PaginatedResponse[Brew]
        404: ErrorResponse
    """
    # Check if teapot exists
    teapot = store.get_teapot(teapot_id)
    if teapot is None:
        return jsonify(ErrorResponse(
            code="NOT_FOUND",
            message="Teapot not found",
        ).model_dump(by_alias=True)), 404

    try:
        query = PaginationQuery(**request.args.to_dict())
    except ValidationError as e:
        return jsonify(ErrorResponse(
            code="VALIDATION_ERROR",
            message="Invalid query parameters",
            details={str(err["loc"][0]): err["msg"] for err in e.errors()},
        ).model_dump(by_alias=True)), 400

    brews, total = store.list_brews_by_teapot(teapot_id, query)
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
