from app.database.connection import database_connection

conn, cursor = database_connection()
cursor.execute("SELECT name, OBJECT_DEFINITION(object_id) FROM sys.triggers WHERE name = 'TGR_INSERE_ACOMPANHAMENTO'")
row = cursor.fetchone()
if row:
    with open('tgr_insere_acomp_full.sql', 'w', encoding='utf-8') as f:
        f.write(row[1])
    print(f"Trigger {row[0]} dumped to tgr_insere_acomp_full.sql")
