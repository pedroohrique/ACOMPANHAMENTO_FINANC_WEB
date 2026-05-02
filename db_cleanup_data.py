from app.database.connection import database_connection

conn, cursor = database_connection()

print("Corrigindo registros de HISTORICO baseados na nova regra...")

# Regra: PIX/DEBITO (não-100) -> Mesmo mês da compra
# Regra: CARTAO (100) -> Mês subsequente

# 1. Corrigir PIX/DEBITO (IDFORMA != 100)
cursor.execute("""
    UPDATE H
    SET H.MES_DEBITO_PARCELA = MONTH(R.DATA_GASTO),
        H.ANO_DEBITO_PARCELA = YEAR(R.DATA_GASTO)
    FROM TB_HISTORICO_FINANC H
    JOIN TB_REG_FINANC R ON R.ID_REGISTRO = H.IDREGISTRO
    WHERE R.IDFORMA_PAGAMENTO != 100
""")
print(f"PIX corrigidos: {cursor.rowcount}")

# 2. Corrigir CARTAO (IDFORMA = 100) - Primeira parcela deve ser Mes + 1
# Nota: Isso é complexo se tiver várias parcelas, mas vamos focar na lógica de 'Subsequente'
cursor.execute("""
    UPDATE H
    SET H.MES_DEBITO_PARCELA = MONTH(DATEADD(MONTH, H.N_PARCELA, R.DATA_GASTO)),
        H.ANO_DEBITO_PARCELA = YEAR(DATEADD(MONTH, H.N_PARCELA, R.DATA_GASTO))
    FROM TB_HISTORICO_FINANC H
    JOIN TB_REG_FINANC R ON R.ID_REGISTRO = H.IDREGISTRO
    WHERE R.IDFORMA_PAGAMENTO = 100
""")
print(f"CARTAO corrigidos: {cursor.rowcount}")

conn.commit()
print("Sincronização de dados finalizada.")
