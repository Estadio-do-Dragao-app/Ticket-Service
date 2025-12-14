import pytest
import os
import sys
import tempfile
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import generate_qr as qr_module

from generate_qr import generate_secure_token

def test_generate_secure_token():
    """Testa geração de token seguro"""
    os.environ['QR_SECRET'] = 'test-secret'
    token = generate_secure_token(123)
    assert ":" in token
    assert len(token.split(":")[1]) == 16

def test_generate_qr(tmp_path):
    """Testa geração de arquivo QR"""
    output_path = tmp_path / "test_qr.png"
    
    result = qr_module.generate_qr(1, str(output_path))
    assert output_path.exists()
    assert result == str(output_path)

def test_main_valid_arguments():
    """Testa execução do script com argumentos válidos"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test_qr.png")
        
        test_args = ["generate_qr.py", "999", output_file]
        
        with patch.object(sys, 'argv', test_args):
            qr_module.main()
        
        assert os.path.exists(output_file), f"Arquivo {output_file} não foi criado"
        os.remove(output_file)

def test_main_missing_argument():
    """Testa execução sem argumentos (deve mostrar help e sair)"""
    captured_output = StringIO()
    
    test_args = ["generate_qr.py"]
    
    with patch.object(sys, 'argv', test_args):
        with patch.object(sys, 'stdout', captured_output):
            with pytest.raises(SystemExit) as exc_info:
                qr_module.main()
    
    assert exc_info.value.code == 1
    
    output = captured_output.getvalue()
    assert "Uso:" in output or "Usage:" in output

def test_main_invalid_ticket_id():
    """Testa com ticket_id inválido (não numérico)"""
    captured_output = StringIO()
    
    test_args = ["generate_qr.py", "abc"]
    
    with patch.object(sys, 'argv', test_args):
        with patch.object(sys, 'stdout', captured_output):
            with pytest.raises(SystemExit) as exc_info:
                qr_module.main()
    
    assert exc_info.value.code == 1
    
    output = captured_output.getvalue()
    # Procura por qualquer mensagem de erro relacionada a ticket_id
    error_keywords = ["Error", "Erro", "ticket_id", "número", "inteiro", "integer"]
    assert any(keyword in output for keyword in error_keywords)

def test_main_default_output():
    """Testa execução sem especificar arquivo de output"""
    test_args = ["generate_qr.py", "888"]
    
    with patch.object(sys, 'argv', test_args):
        qr_module.main()
    
    expected_file = "ticket_888_qr.png"
    assert os.path.exists(expected_file), f"Arquivo padrão {expected_file} não criado"
    
    os.remove(expected_file)

def test_generate_qr_return_value():
    """Testa que generate_qr retorna o caminho do arquivo"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test_return.png")
        
        result = qr_module.generate_qr(777, output_file)
        
        assert result == output_file
        assert os.path.exists(output_file)