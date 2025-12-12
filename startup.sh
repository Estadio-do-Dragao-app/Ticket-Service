#!/bin/bash
set -e

# Wait for PostgreSQL
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; do
  sleep 2
done

# Wait for tables
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1 FROM tickets LIMIT 1;" > /dev/null 2>&1; do
  sleep 2
done

# Generate QR codes
python3 << 'EOF'
import os
import psycopg2
import qrcode
import hmac
import hashlib

def generate_secure_token(ticket_id: int) -> str:
    secret = os.getenv('QR_SECRET', 'default-secret-key')
    message = f"{ticket_id}".encode()
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()[:16]
    return f"{ticket_id}:{signature}"

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT')
)
cur = conn.cursor()
cur.execute("SELECT id FROM tickets")
ticket_ids = [row[0] for row in cur.fetchall()]
cur.close()
conn.close()

os.makedirs('/app/qr_codes', exist_ok=True)
for ticket_id in ticket_ids:
    token = generate_secure_token(ticket_id)
    qr = qrcode.make(token)
    qr.save(f'/app/qr_codes/ticket_{ticket_id}_qr.png')
EOF

# Start FastAPI
exec uvicorn api_handler:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload
