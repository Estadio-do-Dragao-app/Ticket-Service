import pytest
import json
import hmac
import hashlib
import os
from fastapi.testclient import TestClient
from api_handler import app

# Fixture para o cliente de teste
@pytest.fixture
def client():
    return TestClient(app)

# Fixture para secret do QR (deve ser igual ao do ambiente)
@pytest.fixture
def qr_secret():
    return os.getenv('QR_SECRET', 'test-secret-key-for-testing-only')

# Função para gerar token QR (igual à do api_handler)
def generate_qr_token(ticket_id: int, secret: str) -> str:
    signature = hmac.new(
        secret.encode(),
        str(ticket_id).encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    return f"{ticket_id}:{signature}"

def test_get_ticket(client):
    """Testa obtenção de ticket por ID"""
    response = client.get("/ticket/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "event_id" in data

def test_create_ticket(client):
    """Testa criação de novo ticket - enviar ID 0 (será ignorado)"""
    new_ticket = {
        "id": 0,  # Enviar 0, será ignorado pelo banco (serial)
        "event_id": 1,
        "gates_open": "2024-09-15T19:00:00",
        "gate_id": "Gate A",
        "row_id": "Row 6",
        "seat_id": "Seat 15",
        "sector_id": "Norte",
        "ticket_type": "VIP",
        "state": True,
        "seat_node_id": "Seat-Norte-T0-R06-15"
    }
    
    response = client.post("/ticket/", json=new_ticket)
    assert response.status_code == 200
    data = response.json()
    assert data["seat_id"] == "Seat 15"
    assert data["id"] > 0

def test_scan_qr_code(client, qr_secret):
    """Testa leitura de QR code"""
    ticket_id = 1
    token = generate_qr_token(ticket_id, qr_secret)
    
    response = client.get(f"/ticket/scan/{token}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ticket_id

def test_reset_seats(client):
    """Testa reset de todos os assentos"""
    response = client.patch("/tickets/reset")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_ticket_not_found(client):
    """Testa erro quando ticket não existe"""
    response = client.get("/ticket/99999")
    assert response.status_code == 404