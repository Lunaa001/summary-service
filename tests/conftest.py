"""
Pytest configuration and fixtures for tests
"""
import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch):
    """Mock environment variables for all tests"""
    monkeypatch.setenv('MODEL_API_KEY', 'test-key-12345')
    monkeypatch.setenv('MODEL_API_BASE_URL', 'https://ai.cloud.um.edu.ar/api/v1')
    monkeypatch.setenv('IA_MODEL', 'gemma-2-9b-it')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://test:test@localhost/test')
