from app.database.connection import database_connection
import pyodbc

try:
    res = database_connection()
    if res is None:
        print("database_connection retornou None")
    else:
        conn, cursor = res
        cursor.execute("SELECT name FROM sys.tables")
        for row in cursor.fetchall():
            print(row[0])
except Exception as e:
    print(f"Erro: {e}")
