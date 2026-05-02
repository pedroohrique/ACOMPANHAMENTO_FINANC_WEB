import json
import os
from app.database.connection import database_connection

REC_PATH = 'app/database/recorrencias.json'

def sync_recurrences():
    if not os.path.exists(REC_PATH):
        print("Arquivo de recorrencias nao encontrado.")
        return
        
    with open(REC_PATH, 'r') as f:
        ids = json.load(f) # It's a list [1, 2, 3]
        
    conn, cursor = database_connection()
    
    # Reset
    cursor.execute("UPDATE TB_REG_FINANC SET FLAG_RECORRENTE = 0")
    
    if ids:
        placeholders = ','.join(['?'] * len(ids))
        cursor.execute(f"UPDATE TB_REG_FINANC SET FLAG_RECORRENTE = 1 WHERE ID_REGISTRO IN ({placeholders})", ids)
        
    conn.commit()
    print(f"Sincronizados {len(ids)} registros como recorrentes no banco de dados.")

if __name__ == "__main__":
    sync_recurrences()
