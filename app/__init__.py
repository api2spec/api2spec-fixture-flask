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
