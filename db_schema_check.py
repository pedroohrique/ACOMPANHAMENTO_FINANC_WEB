from app.database.connection import database_connection
conn, cursor = database_connection()
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TB_FLUXO_CAIXA'")
for row in cursor.fetchall():
    print(row)
