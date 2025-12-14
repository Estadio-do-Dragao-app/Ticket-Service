import pytest
from generate_qr import generate_secure_token, generate_qr
import os

def test_generate_secure_token():
    """Testa geração de token seguro"""
    os.environ['QR_SECRET'] = 'test-secret'
    token = generate_secure_token(123)
    assert ":" in token  # Deve conter separador
    assert len(token.split(":")[1]) == 16  # Assinatura de 16 chars

def test_generate_qr(tmp_path):
    """Testa geração de arquivo QR"""
    output_path = tmp_path / "test_qr.png"
    result = generate_qr(1, str(output_path))
    assert output_path.exists()