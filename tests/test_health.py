"""Tests for health check routes."""

import pytest
from flask.testing import FlaskClient


class TestHealth:
    """Tests for GET /health."""

    def test_health(self, client: FlaskClient) -> None:
        """Test basic health check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


class TestLiveness:
    """Tests for GET /health/live."""

    def test_liveness(self, client: FlaskClient) -> None:
        """Test liveness probe."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"


class TestReadiness:
    """Tests for GET /health/ready."""

    def test_readiness(self, client: FlaskClient) -> None:
        """Test readiness probe."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "checks" in data
        assert len(data["checks"]) == 2

        # Verify check structure
        for check in data["checks"]:
            assert "name" in check
            assert "status" in check


class TestTeapotEndpoint:
    """Tests for GET /brew (TIF 418 signature)."""

    def test_brew_returns_418(self, client: FlaskClient) -> None:
        """Test that /brew returns 418 I'm a teapot."""
        response = client.get("/brew")

        assert response.status_code == 418
        data = response.get_json()
        assert data["error"] == "I'm a teapot"
        assert "TIF-compliant" in data["message"]
        assert data["spec"] == "https://teapotframework.dev"

    def test_brew_is_tif_compliant(self, client: FlaskClient) -> None:
        """Test TIF compliance message."""
        response = client.get("/brew")

        assert response.status_code == 418
        data = response.get_json()
        assert "cannot brew coffee" in data["message"]
