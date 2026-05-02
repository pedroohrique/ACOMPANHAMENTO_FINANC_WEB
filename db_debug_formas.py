from app.database.connection import database_connection

conn, cursor = database_connection()
print("--- Detalhes das Formas de Pagamento em MAIO ---")
cursor.execute("""
    SELECT R.DESCRICAO, H.VL_PARCELA, R.IDFORMA_PAGAMENTO, FP.DESCRICAO, R.DATA_GASTO
    FROM TB_HISTORICO_FINANC H
    JOIN TB_REG_FINANC R ON R.ID_REGISTRO = H.IDREGISTRO
    JOIN TB_FORMA_PAGAMENTO FP ON R.IDFORMA_PAGAMENTO = FP.ID_FORMA
    WHERE H.MES_DEBITO_PARCELA = 5 AND H.ANO_DEBITO_PARCELA = 2026
""")
for row in cursor.fetchall():
    print(f"Desc: {row[0]}, Valor: {row[1]}, ID_Forma: {row[2]}, Forma: {row[3]}, Gasto: {row[4]}")
