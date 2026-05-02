import pyodbc
from app.database.connection import database_connection

conn, cursor = database_connection()

cursor.execute("""
SELECT name, object_definition(object_id) as definition 
FROM sys.triggers 
WHERE name IN ('TGR_INSERE_ACOMPANHAMENTO', 'TGR_APLICACAO_FINANC', 'TGR_ATT_REGISTROS_FINANCEIROS');
""")
for row in cursor.fetchall():
    print(f"================ TRIGGER: {row[0]} ================")
    print(row[1])
