"""Tests for FastAPI endpoints."""

import pytest
from fastapi import status


class TestHealthEndpoint:
    def test_health_returns_ok(self, test_client):
        resp = test_client.get("/health")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ok"}

    def test_health_method_not_allowed(self, test_client):
        resp = test_client.post("/health")
        assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestGenerateEndpoint:
    def test_generate_returns_200_with_valid_request(self, test_client):
        resp = test_client.post(
            "/generate",
            json={"clip_path": "/test/anime.mp4", "mode": "hybrid", "max_iterations": 3},
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "result" in data

    def test_generate_with_defaults(self, test_client):
        resp = test_client.post(
            "/generate",
            json={"clip_path": "/test/anime.mp4"},
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "result" in data

    def test_generate_missing_clip_path(self, test_client):
        resp = test_client.post("/generate", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("mode", ["local", "cloud", "hybrid"])
    def test_generate_all_modes(self, test_client, mode):
        resp = test_client.post(
            "/generate",
            json={"clip_path": "/test/anime.mp4", "mode": mode, "max_iterations": 1},
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_generate_with_max_iterations_override(self, test_client):
        resp = test_client.post(
            "/generate",
            json={"clip_path": "/test/anime.mp4", "max_iterations": 5},
        )
        assert resp.status_code == status.HTTP_200_OK
