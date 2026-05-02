from app.database.connection import database_connection

conn, cursor = database_connection()
cursor.execute("""
SELECT name, OBJECT_DEFINITION(object_id) 
FROM sys.triggers 
WHERE parent_id = OBJECT_ID('TB_REG_FINANC')
""")
for row in cursor.fetchall():
    print(f"Trigger: {row[0]}")
    print(row[1])
    print("-" * 50)
