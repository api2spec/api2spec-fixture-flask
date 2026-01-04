"""Tests for brew routes."""

import pytest
from flask.testing import FlaskClient


@pytest.fixture
def teapot_id(client: FlaskClient) -> str:
    """Create a teapot and return its ID."""
    response = client.post(
        "/teapots",
        json={
            "name": "Test Teapot",
            "material": "ceramic",
            "capacityMl": 500,
            "style": "english",
        },
    )
    return response.get_json()["id"]


@pytest.fixture
def tea_id(client: FlaskClient) -> str:
    """Create a tea and return its ID."""
    response = client.post(
        "/teas",
        json={
            "name": "Test Tea",
            "type": "green",
            "steepTempCelsius": 80,
            "steepTimeSeconds": 120,
        },
    )
    return response.get_json()["id"]


class TestListBrews:
    """Tests for GET /brews."""

    def test_list_empty(self, client: FlaskClient) -> None:
        """Test listing brews when none exist."""
        response = client.get("/brews")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_list_with_brews(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test listing brews when some exist."""
        # Create a brew
        client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )

        response = client.get("/brews")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["pagination"]["total"] == 1

    def test_list_with_status_filter(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test filtering brews by status."""
        # Create a brew (starts in preparing status)
        client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )

        response = client.get("/brews?status=preparing")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["status"] == "preparing"

    def test_list_with_teapot_filter(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test filtering brews by teapot ID."""
        # Create a brew
        client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )

        response = client.get(f"/brews?teapotId={teapot_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 1
        assert data["data"][0]["teapotId"] == teapot_id


class TestCreateBrew:
    """Tests for POST /brews."""

    def test_create_success(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test creating a brew successfully."""
        response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
                "notes": "Testing brew",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["teapotId"] == teapot_id
        assert data["teaId"] == tea_id
        assert data["status"] == "preparing"
        assert data["notes"] == "Testing brew"
        assert "id" in data
        assert "startedAt" in data
        assert "createdAt" in data

    def test_create_uses_tea_temp(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test that brew uses tea's steep temp if not provided."""
        response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        # Should use tea's steepTempCelsius (80)
        assert data["waterTempCelsius"] == 80

    def test_create_custom_temp(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test that brew can use custom water temp."""
        response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
                "waterTempCelsius": 75,
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["waterTempCelsius"] == 75

    def test_create_teapot_not_found(self, client: FlaskClient, tea_id: str) -> None:
        """Test 400 when teapot doesn't exist."""
        response = client.post(
            "/brews",
            json={
                "teapotId": "nonexistent-id",
                "teaId": tea_id,
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "NOT_FOUND"
        assert "Teapot" in data["message"]

    def test_create_tea_not_found(self, client: FlaskClient, teapot_id: str) -> None:
        """Test 400 when tea doesn't exist."""
        response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": "nonexistent-id",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "NOT_FOUND"
        assert "Tea" in data["message"]


class TestGetBrew:
    """Tests for GET /brews/<id>."""

    def test_get_success(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test getting a brew by ID."""
        # Create a brew first
        create_response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )
        brew_id = create_response.get_json()["id"]

        response = client.get(f"/brews/{brew_id}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == brew_id

    def test_get_not_found(self, client: FlaskClient) -> None:
        """Test 404 for non-existent brew."""
        response = client.get("/brews/nonexistent-id")

        assert response.status_code == 404


class TestPatchBrew:
    """Tests for PATCH /brews/<id>."""

    def test_patch_status(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test updating brew status."""
        # Create a brew first
        create_response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )
        brew_id = create_response.get_json()["id"]

        response = client.patch(
            f"/brews/{brew_id}",
            json={"status": "steeping"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "steeping"

    def test_patch_notes(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test updating brew notes."""
        # Create a brew first
        create_response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )
        brew_id = create_response.get_json()["id"]

        response = client.patch(
            f"/brews/{brew_id}",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["notes"] == "Updated notes"

    def test_patch_not_found(self, client: FlaskClient) -> None:
        """Test 404 for patching non-existent brew."""
        response = client.patch(
            "/brews/nonexistent-id",
            json={"status": "steeping"},
        )

        assert response.status_code == 404


class TestDeleteBrew:
    """Tests for DELETE /brews/<id>."""

    def test_delete_success(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> None:
        """Test deleting a brew."""
        # Create a brew first
        create_response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )
        brew_id = create_response.get_json()["id"]

        response = client.delete(f"/brews/{brew_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/brews/{brew_id}")
        assert get_response.status_code == 404

    def test_delete_not_found(self, client: FlaskClient) -> None:
        """Test 404 for deleting non-existent brew."""
        response = client.delete("/brews/nonexistent-id")

        assert response.status_code == 404


class TestSteeps:
    """Tests for steep endpoints."""

    @pytest.fixture
    def brew_id(
        self, client: FlaskClient, teapot_id: str, tea_id: str
    ) -> str:
        """Create a brew and return its ID."""
        response = client.post(
            "/brews",
            json={
                "teapotId": teapot_id,
                "teaId": tea_id,
            },
        )
        return response.get_json()["id"]

    def test_list_steeps_empty(self, client: FlaskClient, brew_id: str) -> None:
        """Test listing steeps when none exist."""
        response = client.get(f"/brews/{brew_id}/steeps")

        assert response.status_code == 200
        data = response.get_json()
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_create_steep(self, client: FlaskClient, brew_id: str) -> None:
        """Test creating a steep."""
        response = client.post(
            f"/brews/{brew_id}/steeps",
            json={
                "durationSeconds": 60,
                "rating": 4,
                "notes": "Nice and smooth",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["brewId"] == brew_id
        assert data["steepNumber"] == 1
        assert data["durationSeconds"] == 60
        assert data["rating"] == 4
        assert data["notes"] == "Nice and smooth"

    def test_create_multiple_steeps(self, client: FlaskClient, brew_id: str) -> None:
        """Test that steep numbers increment."""
        # First steep
        response1 = client.post(
            f"/brews/{brew_id}/steeps",
            json={"durationSeconds": 60},
        )
        assert response1.get_json()["steepNumber"] == 1

        # Second steep
        response2 = client.post(
            f"/brews/{brew_id}/steeps",
            json={"durationSeconds": 90},
        )
        assert response2.get_json()["steepNumber"] == 2

        # Third steep
        response3 = client.post(
            f"/brews/{brew_id}/steeps",
            json={"durationSeconds": 120},
        )
        assert response3.get_json()["steepNumber"] == 3

    def test_list_steeps_with_data(self, client: FlaskClient, brew_id: str) -> None:
        """Test listing steeps after creating some."""
        # Create steeps
        client.post(
            f"/brews/{brew_id}/steeps",
            json={"durationSeconds": 60},
        )
        client.post(
            f"/brews/{brew_id}/steeps",
            json={"durationSeconds": 90},
        )

        response = client.get(f"/brews/{brew_id}/steeps")

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 2
        # Should be sorted by steep number
        assert data["data"][0]["steepNumber"] == 1
        assert data["data"][1]["steepNumber"] == 2

    def test_steeps_brew_not_found(self, client: FlaskClient) -> None:
        """Test 404 when brew doesn't exist."""
        response = client.get("/brews/nonexistent-id/steeps")
        assert response.status_code == 404

        response = client.post(
            "/brews/nonexistent-id/steeps",
            json={"durationSeconds": 60},
        )
        assert response.status_code == 404
