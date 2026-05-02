from app.database.connection import database_connection

conn, cursor = database_connection()
print("--- Detalhes em ACOMPANHAMENTO para registros de ABRIL ---")
cursor.execute("""
    SELECT RF.DESCRICAO, AF.DT_COMPRA, AF.DT_PAGAMENTO, RF.IDFORMA_PAGAMENTO
    FROM TB_ACOMPANHAMENTO_FINANC AF
    JOIN TB_REG_FINANC RF ON AF.IDREGISTRO = RF.ID_REGISTRO
    WHERE MONTH(AF.DT_COMPRA) = 4 AND YEAR(AF.DT_COMPRA) = 2026
""")
for row in cursor.fetchall():
    print(f"Desc: {row[0]}, Compra: {row[1]}, Pagamento: {row[2]}, ID_Forma: {row[3]}")
