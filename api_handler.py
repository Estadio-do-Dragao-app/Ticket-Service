from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class Ticket(BaseModel):
    id: int
    event_id: int
    gates_open: str
    gate_id: str
    row_id: str
    seat_id: str
    sector_id: str
    ticket_type: str
    state: bool

db_pool = pool.SimpleConnectionPool(1, 20,
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

def get_db_connection():
    return db_pool.getconn()

def release_db_connection(conn):
    db_pool.putconn(conn)


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
            "INSERT INTO tickets (event_id, gates_open, gate_id, row_id, seat_id, sector_id, ticket_type, state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
            (ticket.event_id, ticket.gates_open, ticket.gate_id, ticket.row_id, ticket.seat_id, ticket.sector_id, ticket.ticket_type, ticket.state)
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
