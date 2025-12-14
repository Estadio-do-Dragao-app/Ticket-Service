import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ['TESTING'] = 'True'
os.environ['QR_SECRET'] = 'test-secret-key-for-testing-only'

from api_handler import app, get_db_pool

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_database():
    """Configuração do banco de dados de teste"""
    original_db_pool = get_db_pool()
    yield