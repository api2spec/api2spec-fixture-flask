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
