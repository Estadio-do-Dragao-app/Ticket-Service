from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import hmac
import hashlib
from datetime import datetime

load_dotenv()

app = FastAPI()

# QR Security Configuration
QR_SECRET = os.getenv("QR_SECRET", "change-this-secret-key")

def generate_qr_token(ticket_id: int) -> str:
    """Gera token seguro para QR code (ticket_id + assinatura HMAC)"""
    signature = hmac.new(
        QR_SECRET.encode(),
        str(ticket_id).encode(),
        hashlib.sha256
    ).hexdigest()[:16]  # Usar apenas 16 chars para QR menor
    return f"{ticket_id}:{signature}"

def validate_qr_token(qr_data: str) -> int:
    """Valida token do QR e retorna ticket_id"""
    try:
        parts = qr_data.strip().split(':')
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid QR format")
        
        ticket_id_str, provided_sig = parts
        ticket_id = int(ticket_id_str)
        
        # Calcular assinatura esperada
        expected_sig = hmac.new(
            QR_SECRET.encode(),
            str(ticket_id).encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        # Comparação segura contra timing attacks
        if not hmac.compare_digest(provided_sig, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid QR signature")
        
        return ticket_id
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID format")

class Ticket(BaseModel):
    id: int
    event_id: int
    gates_open: datetime
    gate_id: str
    row_id: str
    seat_id: str
    sector_id: str
    ticket_type: str
    state: bool
    seat_node_id: str | None = None  # ID do seat no Map-Service (ex: Seat-Norte-T0-R05-12)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

db_pool = None

def get_db_pool():
    """Inicializa pool de conexões de forma lazy"""
    global db_pool
    if db_pool is None:
        db_pool = pool.SimpleConnectionPool(1, 20,
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    return db_pool

def get_db_connection():
    return get_db_pool().getconn()

def release_db_connection(conn):
    get_db_pool().putconn(conn)


@app.get("/ticket/scan/{qr_data}", response_model=Ticket)
async def get_ticket_by_qr(qr_data: str):
    """Endpoint seguro para ler QR code e obter dados do bilhete"""
    ticket_id = validate_qr_token(qr_data)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
        ticket = cursor.fetchone()
        cursor.close()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return dict(ticket)
    finally:
        release_db_connection(conn)


@app.get("/ticket/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
        ticket = cursor.fetchone()
        cursor.close()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return dict(ticket)
    finally:
        release_db_connection(conn)


@app.put("/ticket/{ticket_id}", response_model=Ticket)
async def reserve_ticket(ticket_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("UPDATE tickets SET state = true WHERE id = %s RETURNING *", (ticket_id,))
        updated_ticket = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        if not updated_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return dict(updated_ticket)
    finally:
        release_db_connection(conn)


@app.post("/ticket/", response_model=Ticket)
async def create_ticket(ticket: Ticket):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO tickets (event_id, gates_open, gate_id, row_id, seat_id, sector_id, ticket_type, state, seat_node_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (ticket.event_id, ticket.gates_open, ticket.gate_id, ticket.row_id, ticket.seat_id, ticket.sector_id, ticket.ticket_type, ticket.state, ticket.seat_node_id)
        )
        new_ticket = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        return dict(new_ticket)
    finally:
        release_db_connection(conn)

@app.delete("/ticket/{ticket_id}")
async def delete_ticket(ticket_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        cursor.close()
        return {"message": "Ticket deleted"}
    finally:
        release_db_connection(conn)

@app.patch("/tickets/reset")
async def reset_all_seats():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET state = false")
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        
        return {"message": f"Reset {affected_rows} tickets to unoccupied"}
    finally:
        release_db_connection(conn)
