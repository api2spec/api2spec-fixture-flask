"""Tests for tea routes."""

import pytest
from flask.testing import FlaskClient


class TestListTeas:
    """Tests for GET /teas."""

    def test_list_empty(self, client: FlaskClient) -> None:
        """Test listing teas when none exist."""
        response = client.get("/teas")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_list_with_teas(self, client: FlaskClient) -> None:
        """Test listing teas when some exist."""
        # Create a tea first
        client.post(
            "/teas",
            json={
                "name": "Earl Grey",
                "type": "black",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        response = client.get("/teas")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["pagination"]["total"] == 1

    def test_list_with_type_filter(self, client: FlaskClient) -> None:
        """Test filtering teas by type."""
        # Create teas with different types
        client.post(
            "/teas",
            json={
                "name": "Green Tea",
                "type": "green",
                "steepTempCelsius": 80,
                "steepTimeSeconds": 120,
            },
        )
        client.post(
            "/teas",
            json={
                "name": "Black Tea",
                "type": "black",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        response = client.get("/teas?type=green")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["type"] == "green"

    def test_list_with_caffeine_filter(self, client: FlaskClient) -> None:
        """Test filtering teas by caffeine level."""
        # Create teas with different caffeine levels
        client.post(
            "/teas",
            json={
                "name": "Herbal Tea",
                "type": "herbal",
                "caffeineLevel": "none",
                "steepTempCelsius": 100,
                "steepTimeSeconds": 300,
            },
        )
        client.post(
            "/teas",
            json={
                "name": "Black Tea",
                "type": "black",
                "caffeineLevel": "high",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        response = client.get("/teas?caffeineLevel=none")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["caffeineLevel"] == "none"


class TestCreateTea:
    """Tests for POST /teas."""

    def test_create_success(self, client: FlaskClient) -> None:
        """Test creating a tea successfully."""
        response = client.post(
            "/teas",
            json={
                "name": "Gyokuro",
                "type": "green",
                "origin": "Japan",
                "steepTempCelsius": 60,
                "steepTimeSeconds": 90,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Gyokuro"
        assert data["type"] == "green"
        assert data["origin"] == "Japan"
        assert data["steepTempCelsius"] == 60
        assert data["steepTimeSeconds"] == 90
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_create_default_caffeine_level(self, client: FlaskClient) -> None:
        """Test that caffeine level defaults to medium."""
        response = client.post(
            "/teas",
            json={
                "name": "Generic Tea",
                "type": "black",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["caffeineLevel"] == "medium"

    def test_create_missing_required_field(self, client: FlaskClient) -> None:
        """Test validation error for missing required field."""
        response = client.post(
            "/teas",
            json={
                "name": "Incomplete Tea",
                # Missing type, steepTempCelsius, steepTimeSeconds
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_invalid_type(self, client: FlaskClient) -> None:
        """Test validation error for invalid tea type."""
        response = client.post(
            "/teas",
            json={
                "name": "Invalid Tea",
                "type": "coffee",  # Invalid type
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "VALIDATION_ERROR"

    def test_create_temp_too_low(self, client: FlaskClient) -> None:
        """Test validation error for temperature below minimum."""
        response = client.post(
            "/teas",
            json={
                "name": "Cold Tea",
                "type": "green",
                "steepTempCelsius": 50,  # Below min of 60
                "steepTimeSeconds": 120,
            },
        )

        assert response.status_code == 400


class TestGetTea:
    """Tests for GET /teas/<id>."""

    def test_get_success(self, client: FlaskClient) -> None:
        """Test getting a tea by ID."""
        # Create a tea first
        create_response = client.post(
            "/teas",
            json={
                "name": "Earl Grey",
                "type": "black",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )
        tea_id = create_response.get_json()["id"]

        response = client.get(f"/teas/{tea_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == tea_id
        assert data["name"] == "Earl Grey"

    def test_get_not_found(self, client: FlaskClient) -> None:
        """Test 404 for non-existent tea."""
        response = client.get("/teas/nonexistent-id")

        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == "NOT_FOUND"


class TestUpdateTea:
    """Tests for PUT /teas/<id>."""

    def test_update_success(self, client: FlaskClient) -> None:
        """Test updating a tea."""
        # Create a tea first
        create_response = client.post(
            "/teas",
            json={
                "name": "Original Tea",
                "type": "green",
                "steepTempCelsius": 80,
                "steepTimeSeconds": 120,
            },
        )
        tea_id = create_response.get_json()["id"]

        response = client.put(
            f"/teas/{tea_id}",
            json={
                "name": "Updated Tea",
                "type": "black",
                "caffeineLevel": "high",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Updated Tea"
        assert data["type"] == "black"
        assert data["caffeineLevel"] == "high"

    def test_update_not_found(self, client: FlaskClient) -> None:
        """Test 404 for updating non-existent tea."""
        response = client.put(
            "/teas/nonexistent-id",
            json={
                "name": "Updated Tea",
                "type": "black",
                "caffeineLevel": "high",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )

        assert response.status_code == 404


class TestPatchTea:
    """Tests for PATCH /teas/<id>."""

    def test_patch_success(self, client: FlaskClient) -> None:
        """Test partially updating a tea."""
        # Create a tea first
        create_response = client.post(
            "/teas",
            json={
                "name": "Original Tea",
                "type": "green",
                "steepTempCelsius": 80,
                "steepTimeSeconds": 120,
            },
        )
        tea_id = create_response.get_json()["id"]

        response = client.patch(
            f"/teas/{tea_id}",
            json={"name": "Patched Tea"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Patched Tea"
        # Other fields should remain unchanged
        assert data["type"] == "green"
        assert data["steepTempCelsius"] == 80

    def test_patch_not_found(self, client: FlaskClient) -> None:
        """Test 404 for patching non-existent tea."""
        response = client.patch(
            "/teas/nonexistent-id",
            json={"name": "Patched Tea"},
        )

        assert response.status_code == 404


class TestDeleteTea:
    """Tests for DELETE /teas/<id>."""

    def test_delete_success(self, client: FlaskClient) -> None:
        """Test deleting a tea."""
        # Create a tea first
        create_response = client.post(
            "/teas",
            json={
                "name": "To Delete",
                "type": "black",
                "steepTempCelsius": 95,
                "steepTimeSeconds": 240,
            },
        )
        tea_id = create_response.get_json()["id"]

        response = client.delete(f"/teas/{tea_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/teas/{tea_id}")
        assert get_response.status_code == 404

    def test_delete_not_found(self, client: FlaskClient) -> None:
        """Test 404 for deleting non-existent tea."""
        response = client.delete("/teas/nonexistent-id")

        assert response.status_code == 404
