from app.database.connection import database_connection
conn, cursor = database_connection()
cursor.execute("SELECT definition FROM sys.sql_modules WHERE object_id = OBJECT_ID('TGR_ATT_ACOMPANHAMENTO')")
text = cursor.fetchone()[0]
with open('tgr_att_acomp.sql', 'w') as f:
    f.write(text)
