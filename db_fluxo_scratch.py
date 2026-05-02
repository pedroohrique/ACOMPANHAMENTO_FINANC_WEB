import pyodbc
from app.database.connection import database_connection

conn, cursor = database_connection()

cursor.execute("""
SELECT name, object_definition(object_id) as definition 
FROM sys.triggers 
WHERE object_definition(object_id) LIKE '%TB_FLUXO_CAIXA%';
""")
for row in cursor.fetchall():
    print(f"================ TRIGGER: {row[0]} ================")
    print(row[1])

print("\n\n--- Also checking FLUXO_CAIXA data logic ---")
cursor.execute("SELECT name FROM sys.procedures WHERE object_definition(object_id) LIKE '%TB_FLUXO_CAIXA%'")
for row in cursor.fetchall():
    print(f"Proc: {row[0]}")
