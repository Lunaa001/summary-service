"""Tests for health endpoint behavior"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_ok():
    """Health should be OK when DB check succeeds"""
    with patch("main.check_db") as check_db:
        check_db.return_value = None
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["components"]["database"] == "ok"


def test_health_db_failure():
    """Health should be unavailable when DB check fails"""
    with patch("main.check_db", side_effect=Exception("db down")):
        response = client.get("/health")

    assert response.status_code == 503


def test_health_deep_ai_failure():
    """Deep health should be unavailable when AI check fails"""
    with patch("main.check_db") as check_db, patch(
        "main.AIService.test_connection",
        side_effect=Exception("ai down"),
    ):
        check_db.return_value = None
        response = client.get("/health?deep=true")

    assert response.status_code == 503
