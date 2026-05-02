from app.database.connection import database_connection

conn, cursor = database_connection()
print("--- Registros em HISTORICO para MAIO (Mes 5) ---")
cursor.execute("""
    SELECT R.DESCRICAO, H.VL_PARCELA, H.MES_DEBITO_PARCELA, R.DATA_GASTO
    FROM TB_HISTORICO_FINANC H
    JOIN TB_REG_FINANC R ON R.ID_REGISTRO = H.IDREGISTRO
    WHERE H.MES_DEBITO_PARCELA = 5 AND H.ANO_DEBITO_PARCELA = 2026
""")
total = 0
for row in cursor.fetchall():
    print(f"Desc: {row[0]}, Valor: {row[1]}, Mes: {row[2]}, Gasto: {row[3]}")
    total += float(row[1])
print(f"TOTAL MAIO: {total}")
