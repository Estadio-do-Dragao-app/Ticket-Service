"""
Script para verificar a conexão e estrutura do banco de dados
"""
import os
import psycopg2

def check_database():
    """Verifica conexão e estrutura do banco de dados"""
    print("Verificando banco de dados...")
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'test_db'),
            user=os.getenv('DB_USER', 'test_user'),
            password=os.getenv('DB_PASSWORD', 'test_password'),
            port=os.getenv('DB_PORT', 5432)
        )
        print("Conexão estabelecida com sucesso")
        
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        print(f"Tabela 'events' existe com {event_count} registros")
        
        cursor.execute("SELECT COUNT(*) FROM tickets")
        ticket_count = cursor.fetchone()[0]
        print(f"Tabela 'tickets' existe com {ticket_count} registros")
        
        cursor.close()
        conn.close()
        print("Verificação do banco de dados concluída com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro ao verificar banco de dados: {e}")
        return False

if __name__ == "__main__":
    success = check_database()
    exit(0 if success else 1)