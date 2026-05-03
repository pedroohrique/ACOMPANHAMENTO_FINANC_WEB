from app.database.connection import database_connection
from app.utils.logger import log_builder

log = log_builder("querys.py")

def payment_method_map(shared_cursor=None) -> dict:
    if shared_cursor:
        query = "SELECT DESCRICAO, ID_FORMA FROM TB_FORMA_PAGAMENTO"
        shared_cursor.execute(query)
        retorno_query = shared_cursor.fetchall()
        return {linha[0]:linha[1] for linha in retorno_query}
    
    conn_res = database_connection()
    if not conn_res: return {}
    connection, cursor = conn_res
    try:        
        query = "SELECT DESCRICAO, ID_FORMA FROM TB_FORMA_PAGAMENTO"
        cursor.execute(query)
        retorno_query = cursor.fetchall()
        return {linha[0]:linha[1] for linha in retorno_query}
    except Exception as e:
        log.error(f"Falha ao executar a query: {e}")
        return {}
    finally:
        cursor.close()
        connection.close() # FECHAMENTO RIGOROSO
        
def category_map(shared_cursor=None) -> dict:
    if shared_cursor:
        query = "SELECT DESCRICAO, ID_CATEGORIA FROM TB_CATEGORIA"
        shared_cursor.execute(query)
        retorno_query = shared_cursor.fetchall()
        return {linha[0]:linha[1] for linha in retorno_query}

    conn_res = database_connection()
    if not conn_res: return {}
    connection, cursor = conn_res
    try:        
        query = "SELECT DESCRICAO, ID_CATEGORIA FROM TB_CATEGORIA"
        cursor.execute(query)
        retorno_query = cursor.fetchall()
        return {linha[0]:linha[1] for linha in retorno_query}
    except Exception as e:
        log.error(f"Erro ao executar a query: {e}")
        return {}
    finally:
        cursor.close()
        connection.close() # FECHAMENTO RIGOROSO

def deleta_item_treeview(id):
    conn_res = database_connection()
    if not conn_res: return
    connection, cursor = conn_res
    query = "DELETE FROM TB_REG_FINANC WHERE ID_REGISTRO = ?"
    try:
        cursor.execute(query, (id,))
        connection.commit()
    except Exception as e:
        log.error(f"Falha ao excluir o registro: {id}, erro: {e}")
    finally:
        cursor.close()
        connection.close() # FECHAMENTO RIGOROSO

def with_no_filter():
    return """SELECT
                CONVERT(VARCHAR, AF.DT_COMPRA, 103) AS "DT Compra",
                CONVERT(VARCHAR, AF.DT_PAGAMENTO, 103) AS "DT Pagamento",
                AF.VALOR_TOTAL "Total",
                AF.VALOR_PARCELA "Valor Parcela",
                AF.VALOR_PENDENTE "Valor Pendente",
                C.DESCRICAO "Categoria",
                RF.DESCRICAO "Descrição",
                RF.LOCAL_GASTO "Local",
                RF.ID_REGISTRO "IDREGISTRO",
                FP.DESCRICAO,
                RF.PARCELAMENTO,
                RF.N_PARCELAS
            FROM 
                TB_ACOMPANHAMENTO_FINANC AF
                JOIN TB_CATEGORIA C ON AF.IDCATEGORIA = C.ID_CATEGORIA
                JOIN TB_REG_FINANC RF ON AF.IDREGISTRO = RF.ID_REGISTRO
                JOIN TB_FORMA_PAGAMENTO FP ON RF.IDFORMA_PAGAMENTO = FP.ID_FORMA
            ORDER BY AF.DT_COMPRA DESC"""

def fg_total_exp(params, shared_cursor=None):
    query = """SELECT SUM(THF.VL_PARCELA) FROM TB_HISTORICO_FINANC THF
               JOIN TB_REG_FINANC TRF ON TRF.ID_REGISTRO = THF.IDREGISTRO
               WHERE TRF.IDCATEGORIA NOT IN (800, 900) AND THF.MES_DEBITO_PARCELA = ? AND THF.ANO_DEBITO_PARCELA = ?
               GROUP BY THF.MES_DEBITO_PARCELA, THF.ANO_DEBITO_PARCELA;"""
    if shared_cursor:
        shared_cursor.execute(query, params)
        r = shared_cursor.fetchone()
        return r[0] if r else 0
    
    conn_res = database_connection()
    if not conn_res: return 0
    connection, cursor = conn_res
    try:
        cursor.execute(query, params)
        r = cursor.fetchone()
        return r[0] if r else 0
    finally:
        cursor.close()
        connection.close()

def fg_spent_by_category(params, shared_cursor=None):
    query = """SELECT T1.DESCRICAO, COALESCE(SUM(T3.VL_PARCELA), 0) FROM TB_CATEGORIA T1
               LEFT JOIN TB_REG_FINANC T2 ON T2.IDCATEGORIA = T1.ID_CATEGORIA
               LEFT JOIN TB_HISTORICO_FINANC T3 ON T3.IDREGISTRO = T2.ID_REGISTRO
               AND T3.MES_DEBITO_PARCELA = ? AND T3.ANO_DEBITO_PARCELA = ?
               GROUP BY T1.DESCRICAO;"""
    if shared_cursor:
        shared_cursor.execute(query, params)
        return {item[0]: item[1] for item in shared_cursor.fetchall()}

    conn_res = database_connection()
    if not conn_res: return {}
    connection, cursor = conn_res
    try:
        cursor.execute(query, params)
        return {item[0]: item[1] for item in cursor.fetchall()}
    finally:
        cursor.close()
        connection.close()

def fg_outstanding_debts(params, shared_cursor=None):
    query = """SELECT DISTINCT T2.DESCRICAO, T3.NM_MES, T3.ANO, T4.QT_PARCELAS_PENDENTES,
               T4.VALOR_TOTAL, T4.VALOR_PARCELA, T4.VALOR_PENDENTE,
               DATENAME(MONTH, DATEADD(MONTH, T4.QT_PARCELAS - 1, T4.DT_COMPRA)),
               YEAR(DATEADD(MONTH, T4.QT_PARCELAS - 1, T4.DT_COMPRA)),
               T2.ID_REGISTRO
               FROM TB_HISTORICO_FINANC T1
               JOIN TB_REG_FINANC T2 ON T2.ID_REGISTRO = T1.IDREGISTRO
               JOIN DIM_TEMPO T3 ON T3.ID_DATA = T2.IDDATA
               JOIN TB_ACOMPANHAMENTO_FINANC T4 ON T4.IDREGISTRO = T1.IDREGISTRO
               WHERE T4.QT_PARCELAS_PENDENTES > ? AND T4.QT_PARCELAS > ?;"""
    if shared_cursor:
        shared_cursor.execute(query, params)
        return shared_cursor.fetchall()

    conn_res = database_connection()
    if not conn_res: return []
    connection, cursor = conn_res
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def fg_value_pending(params, shared_cursor=None):
    query = """SELECT SUM(VALOR_PENDENTE) FROM TB_ACOMPANHAMENTO_FINANC WHERE QT_PARCELAS > ? AND QT_PARCELAS_PENDENTES > ?"""
    if shared_cursor:
        shared_cursor.execute(query, params)
        r = shared_cursor.fetchone()
        return r[0] if r else 0

    conn_res = database_connection()
    if not conn_res: return 0
    connection, cursor = conn_res
    try:
        cursor.execute(query, params)
        r = cursor.fetchone()
        return r[0] if r else 0
    finally:
        cursor.close()
        connection.close()

def fg_monthly_summary(params, shared_cursor=None):
    query = """WITH CTE AS (
            SELECT THF.MES_DEBITO_PARCELA, THF.ANO_DEBITO_PARCELA, SUM(THF.VL_PARCELA) AS TOTAL_MENSAL,
            COUNT(*) AS QTD_TRANSACOES, MAX(THF.VL_PARCELA) AS MAIOR_GASTO
            FROM TB_HISTORICO_FINANC THF JOIN TB_REG_FINANC TRF ON TRF.ID_REGISTRO = THF.IDREGISTRO
            WHERE TRF.IDCATEGORIA NOT IN (800, 900) AND ANO_DEBITO_PARCELA = ?
            GROUP BY THF.MES_DEBITO_PARCELA, THF.ANO_DEBITO_PARCELA
        )
        SELECT 
            CASE CTE.MES_DEBITO_PARCELA WHEN 1 THEN 'JAN' WHEN 2 THEN 'FEV' WHEN 3 THEN 'MAR' WHEN 4 THEN 'ABR' WHEN 5 THEN 'MAI' WHEN 6 THEN 'JUN' WHEN 7 THEN 'JUL' WHEN 8 THEN 'AGO' WHEN 9 THEN 'SET' WHEN 10 THEN 'OUT' WHEN 11 THEN 'NOV' WHEN 12 THEN 'DEZ' END,
            CTE.ANO_DEBITO_PARCELA, 7500.0, CTE.TOTAL_MENSAL, 7500.0 - CTE.TOTAL_MENSAL, (CTE.TOTAL_MENSAL / 7500.0) * 100,
            CTE.QTD_TRANSACOES, CTE.MAIOR_GASTO, SUM(CTE.TOTAL_MENSAL) OVER (ORDER BY CTE.MES_DEBITO_PARCELA),
            CTE.TOTAL_MENSAL - LAG(CTE.TOTAL_MENSAL) OVER (ORDER BY CTE.MES_DEBITO_PARCELA), NULL FROM CTE ORDER BY 2, 1;"""
    if shared_cursor:
        shared_cursor.execute(query, params)
        return shared_cursor.fetchall()

    conn_res = database_connection()
    if not conn_res: return []
    connection, cursor = conn_res
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def query_money_flow(params, shared_cursor=None):
    query = """SELECT 
            (SELECT COALESCE(SUM(VALOR), 0) FROM TB_FLUXO_CAIXA WHERE MONTH(DATA_REGISTRO) = ? AND YEAR(DATA_REGISTRO) = ? AND IDCATEGORIA = 800),
            (SELECT COALESCE(SUM(VALOR), 0) FROM TB_FLUXO_CAIXA WHERE MONTH(DATA_REGISTRO) = ? AND YEAR(DATA_REGISTRO) = ? AND IDCATEGORIA != 800),
            0,
            (SELECT TOP 1 COALESCE(VALOR_ACUMULADO, 0) FROM TB_FLUXO_CAIXA ORDER BY ID_FLUXO DESC)"""
    # Ajuste de params para a query simplificada
    p = (params[0], params[1], params[0], params[1])
    if shared_cursor:
        shared_cursor.execute(query, p)
        return shared_cursor.fetchall()

    conn_res = database_connection()
    if not conn_res: return []
    connection, cursor = conn_res
    try:
        cursor.execute(query, p)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

def record_financial(array):
    conn_res = database_connection()
    if not conn_res: return
    connection, cursor = conn_res
    query = """INSERT INTO TB_REG_FINANC (DATA_REGISTRO, DATA_GASTO, VALOR, DESCRICAO, LOCAL_GASTO, PARCELAMENTO, N_PARCELAS, IDCATEGORIA, IDFORMA_PAGAMENTO) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    try:
        cursor.execute(query, (array["dt_registro"], array["dt_gasto"], array["valor"], array["desc"], array["desc_local"], array["flag_parcelamento"], array["qt_parcelas"], array["desc_categoria"], array["forma_pagamento"]))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_financial(array, id_registro):
    conn_res = database_connection()
    if not conn_res: return
    connection, cursor = conn_res
    query = """UPDATE TB_REG_FINANC SET DATA_GASTO=?, VALOR=?, DESCRICAO=?, LOCAL_GASTO=?, IDCATEGORIA=?, IDFORMA_PAGAMENTO=?, PARCELAMENTO=?, N_PARCELAS=? WHERE ID_REGISTRO=?"""
    try:
        cursor.execute(query, (array["dt_gasto"], array["valor"], array["desc"], array["desc_local"], array["desc_categoria"], array["forma_pagamento"], array["flag_parcelamento"], array["qt_parcelas"], id_registro))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
