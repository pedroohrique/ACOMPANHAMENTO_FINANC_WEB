from app.database.connection import database_connection
conn, cursor = database_connection()
cursor.execute("""
    SELECT name, definition 
    FROM sys.triggers t 
    JOIN sys.sql_modules m ON t.object_id = m.object_id 
    WHERE m.definition LIKE '%900%'
""")
for row in cursor.fetchall():
    print(f"--- TRIGGER: {row[0]} ---")
    print(row[1])
