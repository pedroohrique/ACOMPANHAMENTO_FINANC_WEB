from app.database.connection import database_connection
conn, cursor = database_connection()
cursor.execute("SELECT DISTINCT PARCELAMENTO, N_PARCELAS FROM TB_REG_FINANC")
for row in cursor.fetchall():
    print(row)
