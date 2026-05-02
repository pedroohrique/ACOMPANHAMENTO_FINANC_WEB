import pyodbc
from app.database.connection import database_connection
import json

conn, cursor = database_connection()

print("--- Checking Users ---")
try:
    with open('app/database/users.json', 'r') as f:
        print(f.read())
except Exception as e:
    print(f"No users file: {e}")

print("\n--- Checking Data for May 2026 ---")
cursor.execute("""
SELECT COUNT(*) FROM TB_REG_FINANC WHERE MONTH(DATA_GASTO) = 5 AND YEAR(DATA_GASTO) = 2026;
""")
print(f"Registros em TB_REG_FINANC: {cursor.fetchone()[0]}")

cursor.execute("""
SELECT COUNT(*) FROM TB_HISTORICO_FINANC WHERE MES_DEBITO_PARCELA = 5 AND ANO_DEBITO_PARCELA = 2026;
""")
print(f"Registros em TB_HISTORICO_FINANC: {cursor.fetchone()[0]}")

cursor.execute("""
SELECT TOP 5 ID_REGISTRO, DATA_GASTO, VALOR, DESCRICAO FROM TB_REG_FINANC WHERE MONTH(DATA_GASTO) = 5 AND YEAR(DATA_GASTO) = 2026;
""")
print("Amostra TB_REG_FINANC:", cursor.fetchall())

print("\n--- Verificando FLUXO_CAIXA ---")
cursor.execute("""
SELECT COUNT(*) FROM TB_FLUXO_CAIXA WHERE MONTH(DATA_REGISTRO) = 5 AND YEAR(DATA_REGISTRO) = 2026;
""")
print(f"Registros em TB_FLUXO_CAIXA: {cursor.fetchone()[0]}")

print("\n--- Recorrências Atuais ---")
try:
    with open('app/database/recorrencias.json', 'r') as f:
        print(f.read())
except Exception as e:
    print(e)
