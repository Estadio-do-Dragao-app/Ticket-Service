"""
Testes básicos de banco de dados
"""
import psycopg2
import os

def test_database_connection():
    """Testa conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'test_db'),
            user=os.getenv('DB_USER', 'test_user'),
            password=os.getenv('DB_PASSWORD', 'test_password'),
            port=os.getenv('DB_PORT', 5432)
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        assert result[0] == 1
        print("Conexão com banco de dados bem-sucedida")
    except Exception as e:
        print(f"Erro na conexão com banco de dados: {e}")
        raise

def test_tables_exist():
    """Verifica se as tabelas foram criadas"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'test_db'),
            user=os.getenv('DB_USER', 'test_user'),
            password=os.getenv('DB_PASSWORD', 'test_password'),
            port=os.getenv('DB_PORT', 5432)
        )
        cursor = conn.cursor()
        
        # Verifica tabela events
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'events'
            )
        """)
        events_exists = cursor.fetchone()[0]
        assert events_exists, "Tabela 'events' não existe"
        
        # Verifica tabela tickets
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tickets'
            )
        """)
        tickets_exists = cursor.fetchone()[0]
        assert tickets_exists, "Tabela 'tickets' não existe"
        
        cursor.close()
        conn.close()
        print("Tabelas existem no banco de dados")
    except Exception as e:
        print(f"Erro ao verificar tabelas: {e}")
        raise