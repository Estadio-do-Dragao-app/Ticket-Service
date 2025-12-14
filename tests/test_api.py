import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from api_handler import app, generate_qr_token

@pytest.fixture
def client():
    return TestClient(app)

def test_get_ticket(client):
    """Testa obtenção de ticket por ID"""
    response = client.get("/ticket/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "event_id" in data

def test_create_ticket(client):
    """Testa criação de novo ticket"""
    new_ticket = {
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

def test_scan_qr_code(client):
    """Testa leitura de QR code"""
    ticket_id = 1
    token = generate_qr_token(ticket_id)
    
    response = client.get(f"/ticket/scan/{token}")
    assert response.status_code == 200

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