"""Route blueprint registration."""

from flask import Flask

from . import brews, health, teapots, teas


def register_routes(app: Flask) -> None:
    """Register all route blueprints."""
    app.register_blueprint(health.bp)
    app.register_blueprint(teapots.bp)
    app.register_blueprint(teas.bp)
    app.register_blueprint(brews.bp)
