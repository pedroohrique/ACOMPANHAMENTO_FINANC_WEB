from app.database.connection import database_connection
conn, cursor = database_connection()
cursor.execute("SELECT definition FROM sys.sql_modules WHERE object_id = OBJECT_ID('TGR_ATT_REGISTROS_FINANCEIROS')")
print(cursor.fetchone()[0])
