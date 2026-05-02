import pyodbc
from app.database.connection import database_connection

conn, cursor = database_connection()

print("--- Checking Triggers on TB_REG_FINANC ---")
cursor.execute("""
SELECT name, object_definition(object_id) as definition 
FROM sys.triggers 
WHERE parent_id = object_id('TB_REG_FINANC');
""")
for row in cursor.fetchall():
    print(f"Trigger: {row[0]}")
    # print(row[1])  # Might be too long

print("--- Checking Stored Procedures ---")
cursor.execute("""
SELECT name FROM sys.procedures;
""")
for row in cursor.fetchall():
    print(f"Proc: {row[0]}")

