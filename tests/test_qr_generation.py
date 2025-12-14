import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from generate_qr import generate_secure_token, generate_qr

def test_generate_secure_token():
    """Testa geração de token seguro"""
    os.environ['QR_SECRET'] = 'test-secret'
    token = generate_secure_token(123)
    assert ":" in token
    assert len(token.split(":")[1]) == 16

def test_generate_qr(tmp_path):
    """Testa geração de arquivo QR"""
    output_path = tmp_path / "test_qr.png"
    result = generate_qr(1, str(output_path))
    assert output_path.exists()