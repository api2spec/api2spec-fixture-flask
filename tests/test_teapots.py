"""Tests for teapot routes."""

import pytest
from flask.testing import FlaskClient


class TestListTeapots:
    """Tests for GET /teapots."""

    def test_list_empty(self, client: FlaskClient) -> None:
        """Test listing teapots when none exist."""
        response = client.get("/teapots")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["totalPages"] == 0

    def test_list_with_teapots(self, client: FlaskClient) -> None:
        """Test listing teapots when some exist."""
        # Create a teapot first
        client.post(
            "/teapots",
            json={
                "name": "Test Teapot",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )

        response = client.get("/teapots")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["pagination"]["total"] == 1

    def test_list_with_material_filter(self, client: FlaskClient) -> None:
        """Test filtering teapots by material."""
        # Create teapots with different materials
        client.post(
            "/teapots",
            json={
                "name": "Ceramic Pot",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        client.post(
            "/teapots",
            json={
                "name": "Glass Pot",
                "material": "glass",
                "capacityMl": 600,
                "style": "english",
            },
        )

        response = client.get("/teapots?material=ceramic")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["material"] == "ceramic"

    def test_list_with_pagination(self, client: FlaskClient) -> None:
        """Test pagination parameters."""
        # Create multiple teapots
        for i in range(5):
            client.post(
                "/teapots",
                json={
                    "name": f"Teapot {i}",
                    "material": "ceramic",
                    "capacityMl": 500,
                    "style": "english",
                },
            )

        response = client.get("/teapots?page=1&limit=2")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["totalPages"] == 3


class TestCreateTeapot:
    """Tests for POST /teapots."""

    def test_create_success(self, client: FlaskClient) -> None:
        """Test creating a teapot successfully."""
        response = client.post(
            "/teapots",
            json={
                "name": "My Kyusu",
                "material": "clay",
                "capacityMl": 350,
                "style": "kyusu",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "My Kyusu"
        assert data["material"] == "clay"
        assert data["capacityMl"] == 350
        assert data["style"] == "kyusu"
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_with_description(self, client: FlaskClient) -> None:
        """Test creating a teapot with optional description."""
        response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
                "description": "A beautiful teapot",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["description"] == "A beautiful teapot"

    def test_create_default_style(self, client: FlaskClient) -> None:
        """Test that style defaults to english."""
        response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                "material": "ceramic",
                "capacityMl": 500,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["style"] == "english"

    def test_create_missing_required_field(self, client: FlaskClient) -> None:
        """Test validation error for missing required field."""
        response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                # Missing material and capacityMl
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_invalid_material(self, client: FlaskClient) -> None:
        """Test validation error for invalid material."""
        response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                "material": "plastic",  # Invalid material
                "capacityMl": 500,
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_capacity_too_large(self, client: FlaskClient) -> None:
        """Test validation error for capacity exceeding max."""
        response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                "material": "ceramic",
                "capacityMl": 10000,  # Exceeds max of 5000
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"


class TestGetTeapot:
    """Tests for GET /teapots/<id>."""

    def test_get_success(self, client: FlaskClient) -> None:
        """Test getting a teapot by ID."""
        # Create a teapot first
        create_response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        teapot_id = create_response.get_json()["id"]

        response = client.get(f"/teapots/{teapot_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == teapot_id
        assert data["name"] == "My Teapot"

    def test_get_not_found(self, client: FlaskClient) -> None:
        """Test 404 for non-existent teapot."""
        response = client.get("/teapots/nonexistent-id")

        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == "NOT_FOUND"


class TestUpdateTeapot:
    """Tests for PUT /teapots/<id>."""

    def test_update_success(self, client: FlaskClient) -> None:
        """Test updating a teapot."""
        # Create a teapot first
        create_response = client.post(
            "/teapots",
            json={
                "name": "Original Name",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        teapot_id = create_response.get_json()["id"]

        response = client.put(
            f"/teapots/{teapot_id}",
            json={
                "name": "Updated Name",
                "material": "glass",
                "capacityMl": 600,
                "style": "kyusu",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Updated Name"
        assert data["material"] == "glass"
        assert data["capacityMl"] == 600
        assert data["style"] == "kyusu"

    def test_update_not_found(self, client: FlaskClient) -> None:
        """Test 404 for updating non-existent teapot."""
        response = client.put(
            "/teapots/nonexistent-id",
            json={
                "name": "Updated Name",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )

        assert response.status_code == 404

    def test_update_validation_error(self, client: FlaskClient) -> None:
        """Test validation error on update."""
        # Create a teapot first
        create_response = client.post(
            "/teapots",
            json={
                "name": "Original Name",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        teapot_id = create_response.get_json()["id"]

        response = client.put(
            f"/teapots/{teapot_id}",
            json={
                "name": "Updated Name",
                # Missing required fields
            },
        )

        assert response.status_code == 400


class TestPatchTeapot:
    """Tests for PATCH /teapots/<id>."""

    def test_patch_success(self, client: FlaskClient) -> None:
        """Test partially updating a teapot."""
        # Create a teapot first
        create_response = client.post(
            "/teapots",
            json={
                "name": "Original Name",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        teapot_id = create_response.get_json()["id"]

        response = client.patch(
            f"/teapots/{teapot_id}",
            json={"name": "Patched Name"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Patched Name"
        # Other fields should remain unchanged
        assert data["material"] == "ceramic"
        assert data["capacityMl"] == 500

    def test_patch_not_found(self, client: FlaskClient) -> None:
        """Test 404 for patching non-existent teapot."""
        response = client.patch(
            "/teapots/nonexistent-id",
            json={"name": "Patched Name"},
        )

        assert response.status_code == 404


class TestDeleteTeapot:
    """Tests for DELETE /teapots/<id>."""

    def test_delete_success(self, client: FlaskClient) -> None:
        """Test deleting a teapot."""
        # Create a teapot first
        create_response = client.post(
            "/teapots",
            json={
                "name": "To Delete",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        teapot_id = create_response.get_json()["id"]

        response = client.delete(f"/teapots/{teapot_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/teapots/{teapot_id}")
        assert get_response.status_code == 404

    def test_delete_not_found(self, client: FlaskClient) -> None:
        """Test 404 for deleting non-existent teapot."""
        response = client.delete("/teapots/nonexistent-id")

        assert response.status_code == 404


class TestTeapotBrews:
    """Tests for GET /teapots/<teapot_id>/brews."""

    def test_list_brews_for_teapot(self, client: FlaskClient) -> None:
        """Test listing brews for a specific teapot."""
        # Create a teapot
        teapot_response = client.post(
            "/teapots",
            json={
                "name": "My Teapot",
                "material": "ceramic",
                "capacityMl": 500,
                "style": "english",
            },
        )
        teapot_id = teapot_response.get_json()["id"]

        # Create a tea
        tea_response = client.post(
            "/teas",
            json={
                "name": "Green Tea",
                "type": "green",
                "steepTempCelsius": 80,
                "steepTimeSeconds": 120,
            },
        )
        tea_id = tea_response.get_json()["id"]

        # Create a brew for this teapot
        client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )

        response = client.get(f"/teapots/{teapot_id}/brews")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["teapotId"] == teapot_id

    def test_list_brews_teapot_not_found(self, client: FlaskClient) -> None:
        """Test 404 when teapot doesn't exist."""
        response = client.get("/teapots/nonexistent-id/brews")

        assert response.status_code == 404
