#!/usr/bin/env python3
"""
Gera QR codes em lote para todos os bilhetes
Uso: python generate_batch_qr.py [ticket_id_inicial] [ticket_id_final]
"""
import sys
import os
from generate_qr import generate_qr

def generate_batch(start_id: int = 1, end_id: int = None, output_dir: str = "qr_codes"):
    """Gera QR codes para múltiplos bilhetes"""
    
    # Criar diretório de output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Diretório criado: {output_dir}/")
    
    # Se não especificar end_id, gerar apenas para start_id
    if end_id is None:
        end_id = start_id
    
    print(f"\n🎫 Gerando QR codes para bilhetes {start_id} a {end_id}...")
    print("=" * 60)
    
    success_count = 0
    for ticket_id in range(start_id, end_id + 1):
        try:
            output_path = os.path.join(output_dir, f"ticket_{ticket_id}_qr.png")
            generate_qr(ticket_id, output_path)
            success_count += 1
        except Exception as e:
            print(f"❌ Erro ao gerar QR para ticket {ticket_id}: {e}")
    
    print("=" * 60)
    print(f"✅ {success_count} QR codes gerados com sucesso em: {output_dir}/")
    print(f"\n💡 Estes QR codes podem ser impressos nos bilhetes.")

def main():
    if len(sys.argv) == 1:
        print("Uso: python generate_batch_qr.py [start_id] [end_id]")
        print("\nExemplos:")
        print("  python generate_batch_qr.py 1        # Gera apenas ticket 1")
        print("  python generate_batch_qr.py 1 10     # Gera tickets 1 a 10")
        print("  python generate_batch_qr.py 1 100    # Gera tickets 1 a 100")
        sys.exit(1)
    
    try:
        start_id = int(sys.argv[1])
        end_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        generate_batch(start_id, end_id)
        
    except ValueError:
        print("❌ Erro: IDs devem ser números inteiros")
        sys.exit(1)

if __name__ == "__main__":
    main()
