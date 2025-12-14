import pytest
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

# Configura variáveis de ambiente para testes
os.environ['TESTING'] = 'True'
os.environ['QR_SECRET'] = 'test-secret-key-for-testing-only'

@pytest.fixture(scope='session', autouse=True)
def setup_database():
    """Configura o banco de dados de teste antes de todos os testes"""
    print("\nConfigurando banco de dados de teste...")
    
    # Conecta ao banco de dados
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'test_db'),
        user=os.getenv('DB_USER', 'test_user'),
        password=os.getenv('DB_PASSWORD', 'test_password'),
        port=os.getenv('DB_PORT', 5432)
    )
    
    # Executa os scripts SQL
    with open('db/ddl.sql', 'r') as f:
        ddl_sql = f.read()
    
    with open('db/dml.sql', 'r') as f:
        dml_sql = f.read()
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(ddl_sql)
        print("Tabelas criadas com sucesso")
    except Exception as e:
        print(f"Erro ao criar tabelas (pode já existir): {e}")
        conn.rollback()
    
    try:
        cursor.execute(dml_sql)
        print("Dados de teste inseridos com sucesso")
    except Exception as e:
        print(f"Erro ao inserir dados (pode já existir): {e}")
        conn.rollback()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Banco de dados configurado para testes\n")
    yield