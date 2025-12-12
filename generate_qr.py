#!/usr/bin/env python3
"""Gera QR codes seguros com HMAC
Uso: python generate_qr.py <ticket_id>
"""
import sys
import qrcode
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

QR_SECRET = os.getenv("QR_SECRET", "change-this-secret-key")

def generate_secure_token(ticket_id: int) -> str:
    """Gera token seguro (ticket_id + assinatura HMAC)"""
    signature = hmac.new(
        QR_SECRET.encode(),
        str(ticket_id).encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    return f"{ticket_id}:{signature}"

def generate_qr(ticket_id: int, output_path: str = None):
    """Gera QR code com token seguro HMAC"""
    if output_path is None:
        output_path = f"ticket_{ticket_id}_qr.png"
    
    # Gerar token seguro
    secure_token = generate_secure_token(ticket_id)
    
    # Criar QR com o token seguro
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(secure_token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    
    print(f"✅ QR code gerado: {output_path}")
    print(f"   Ticket ID: {ticket_id}")
    print(f"   Token seguro: {secure_token}")
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Uso: python generate_qr.py <ticket_id> [output.png]")
        print("Exemplo: python generate_qr.py 1")
        sys.exit(1)
    
    try:
        ticket_id = int(sys.argv[1])
    except ValueError:
        print("❌ Erro: ticket_id deve ser um número inteiro")
        sys.exit(1)
    
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    generate_qr(ticket_id, output_path)

if __name__ == "__main__":
    main()
