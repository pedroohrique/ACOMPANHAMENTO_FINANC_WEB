from app.database.querys import record_financial
from app.database.connection import database_connection
from datetime import datetime

# Simulating adding an APRIL record TODAY (MAY)
data = {
    "dt_registro": datetime.now(),
    "dt_gasto": "2026-04-15",
    "valor": 555.55,
    "desc": "Teste Discrepancia",
    "desc_local": "Loja Teste",
    "flag_parcelamento": "N",
    "qt_parcelas": 1,
    "desc_categoria": 100, # Alimentacao?
    "forma_pagamento": 200 # Outra forma?
}

print("Inserindo registro de ABRIL...")
record_financial(data)

conn, cursor = database_connection()
cursor.execute("SELECT IDREGISTRO, MES_DEBITO_PARCELA, ANO_DEBITO_PARCELA, VL_PARCELA FROM TB_HISTORICO_FINANC WHERE VL_PARCELA = 555.55")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]}, Mes: {r[1]}, Ano: {r[2]}, Valor: {r[3]}")
