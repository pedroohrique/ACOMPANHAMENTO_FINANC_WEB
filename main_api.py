from fastapi import FastAPI, HTTPException, Body, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import json
import os

RECORRENCIAS_FILE = os.path.join("app", "database", "recorrencias.json")

def get_recorrencias_ids():
    if not os.path.exists(RECORRENCIAS_FILE):
        return []
    try:
        with open(RECORRENCIAS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def toggle_recorrencia_status(id_registro, status):
    ids = get_recorrencias_ids()
    if status and id_registro not in ids:
        ids.append(id_registro)
    elif not status and id_registro in ids:
        ids.remove(id_registro)
    with open(RECORRENCIAS_FILE, "w") as f:
        json.dump(ids, f)
    
    # Sincroniza com o Banco de Dados para os Triggers
    try:
        from app.database.connection import database_connection
        db_res = database_connection()
        if db_res:
            conn, cursor = db_res
            with conn:
                cursor.execute("UPDATE TB_REG_FINANC SET FLAG_RECORRENTE = ? WHERE ID_REGISTRO = ?", (1 if status else 0, id_registro))
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Erro ao sincronizar flag de recorrencia no DB: {e}")

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importações das suas queries originais
from app.database.querys import (
    payment_method_map,
    category_map,
    fg_monthly_summary,
    query_money_flow,
    fg_spent_by_category,
    with_no_filter,
    record_financial,
    update_financial,
    deleta_item_treeview,
    fg_outstanding_debts,
    fg_active_installments,
    fg_value_pending,
    fg_total_exp,
    database_connection
)
app = FastAPI(title="API Acompanhamento Financeiro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURANÇA (JWT) ---
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "pedro_financas_2026_jwt_secret_key_super_segura"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Pula rotas públicas e preflight (OPTIONS)
    if (request.url.path.startswith("/api/auth") or 
        request.method == "OPTIONS" or 
        request.url.path == "/"):
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    
    # --- COMPATIBILIDADE TEMPORÁRIA (Para evitar "Sem Dados" por cache) ---
    # Aceita tokens antigos do sistema anterior enquanto o usuário não atualiza o browser
    if auth_header and (auth_header.startswith("Bearer token_") or "pedro" in auth_header.lower()):
        logger.info(f"Acesso via token legado: {request.url.path}")
        return await call_next(request)
    # ----------------------------------------------------------------------

    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning(f"Acesso negado (Sem Header): {request.url.path}")
        return JSONResponse(status_code=401, content={"detail": "Não autenticado"})
    
    token = auth_header.split(" ")[1]
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return await call_next(request)
    except Exception as e:
        logger.warning(f"Acesso negado (Token Inválido): {e} | Path: {request.url.path}")
        return JSONResponse(status_code=401, content={"detail": "Sessão inválida ou expirada"})

# --- AUXILIARES ---
def get_db_data(query_func, params=None):
    try:
        if params is not None:
            return query_func(params)
        return query_func()
    except Exception as e:
        logger.error(f"Erro ao executar {query_func.__name__}: {e}")
        return None

# --- ROTAS DE CONFIGURAÇÃO ---
@app.get("/api/categorias")
def get_categories():
    return {"categorias": get_db_data(category_map) or {}}

@app.get("/api/formas-pagamento")
def get_payment_methods():
    return {"formas_pagamento": get_db_data(payment_method_map) or {}}

# --- ROTAS DE AUTENTICAÇÃO ---
USERS_FILE = os.path.join("app", "database", "users.json")

def get_users():
    if not os.path.exists(USERS_FILE): return {}
    try:
        with open(USERS_FILE, "r") as f: return json.load(f)
    except: return {}

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f: json.dump(users, f)

@app.post("/api/auth/register")
def register(data: Dict[str, Any]):
    users = get_users()
    email = data.get("email")
    if not email: raise HTTPException(status_code=400, detail="Email obrigatorio")
    if email in users: raise HTTPException(status_code=400, detail="Usuario ja cadastrado")
    
    # Gerar código de verificação
    code = "123456" # Fixo para facilitar ou pode ser random
    logger.info(f"========== CÓDIGO DE VERIFICAÇÃO PARA {email}: {code} ==========")
    
    users[email] = {
        "nome": data.get("nome"),
        "password": data.get("password"),
        "verified": False,
        "verification_code": code
    }
    save_users(users)
    return {"message": "Usuario registrado. Verifique o console para o código."}

@app.post("/api/auth/verify")
def verify(data: Dict[str, Any]):
    users = get_users()
    email = data.get("email")
    code = data.get("code")
    if email not in users:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    if users[email].get("verification_code") != code:
        raise HTTPException(status_code=400, detail="Código inválido")
    
    users[email]["verified"] = True
    save_users(users)
    return {"message": "Email verificado com sucesso"}

@app.post("/api/auth/login")
def login(data: Dict[str, Any]):
    users = get_users()
    email = data.get("email")
    password = data.get("password")
    if email not in users or users[email]["password"] != password:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")
    
    # Gera o token JWT
    access_token = create_access_token(data={"sub": email})
    
    return {
        "access_token": access_token,
        "user": {"nome": users[email]["nome"], "email": email}
    }

# --- ROTAS DE DASHBOARD / RELATÓRIO ---
def parse_currency(value):
    if value is None: return 0.0
    if isinstance(value, (int, float)): return float(value)
    
    # Se for string, remove R$, espaços e caracteres invisíveis
    s = str(value).replace('R$', '').replace(' ', '').replace('\xa0', '').strip()
    if not s: return 0.0
    
    # IDENTIFICAÇÃO DE FORMATO:
    # Se tem vírgula, tratamos como BR: "1.234,56" -> "1234.56"
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    # Se NÃO tem vírgula mas tem ponto, assumimos que o ponto JÁ É o decimal (US)
    # Ex: "1234.56" fica "1234.56". NÃO remover o ponto!
    
    try:
        res = float(s)
        # Log para debug se o valor for muito alto (suspeita de erro de escala)
        if res > 1000000:
            logger.warning(f"Valor suspeito detectado: {res} vindo de original: {value}")
        return res
    except:
        return 0.0

@app.get("/api/resumo-mensal/{ano}")
def get_monthly_summary_route(ano: int):
    resumo = get_db_data(fg_monthly_summary, (ano,))
    if not resumo: return {"resumo": []}
    
    return {"resumo": [{
        "mes": str(linha[0]).strip(), 
        "ano": linha[1], 
        "orcamento": parse_currency(linha[2]), 
        "gasto": parse_currency(linha[3]), 
        "saldo": parse_currency(linha[4]), 
        "percentual": linha[5], 
        "qtd": linha[6], 
        "maior_gasto": linha[7],
        "acumulado": parse_currency(linha[8]), 
        "variacao": linha[9], 
        "percentual_var": linha[10]
    } for linha in resumo]}

@app.get("/api/fluxo-caixa/{ano}/{mes}")
def get_money_flow_route(ano: int, mes: int):
    fluxo = get_db_data(query_money_flow, (mes, ano))
    if not fluxo or not fluxo[0] or fluxo[0][0] is None:
        return {"fluxo": {"vl_entradas": 0, "vl_saidas": 0, "custo_medio_mensal": 0, "saldo_atual": 0}}
    
    l = fluxo[0]
    return {"fluxo": {"vl_entradas": l[0], "vl_saidas": l[1], "custo_medio_mensal": l[2], "saldo_atual": l[3]}}

@app.get("/api/gastos-por-categoria/{ano}/{mes}")
def get_spent_by_category_route(ano: int, mes: int):
    return {"gastos": get_db_data(fg_spent_by_category, (mes, ano)) or {}}

@app.get("/api/debitos-pendentes")
def get_pending_debts():
    debitos = get_db_data(fg_outstanding_debts, (0, 1)) # Parâmetros baseados no file_generator.py
    if not debitos: return {"debitos": []}
    
    return {"debitos": [{
        "descricao": d[0], "mes_compra": d[1], "ano": d[2], "parcelas_pendentes": d[3],
        "valor_total": d[4], "valor_parcela": d[5], "valor_pendente": d[6],
        "mes_ultimo_debito": d[7], "ano_ultimo_debito": d[8]
    } for d in debitos]}

# --- NOVO: ENDPOINT CONSOLIDADO PARA VELOCIDADE ---
@app.get("/api/v2/dashboard-full/{ano}/{mes}")
def get_dashboard_full(ano: int, mes: int):
    try:
        # Busca tudo em uma única conexão se possível ou em chamadas rápidas
        fluxo = get_db_data(query_money_flow, (mes, ano))
        resumo = get_db_data(fg_monthly_summary, (ano,))
        categorias = get_db_data(fg_spent_by_category, (mes, ano))
        debitos = get_db_data(fg_outstanding_debts)
        # transacoes = get_db_data(with_no_filter) # Podemos manter separado se for muito pesado, mas vamos incluir
        
        # Visão Geral Relatório
        report = get_db_data(fg_monthly_summary, (ano,)) # Reutilizando resumo por enquanto ou chamando específico
        
        # Auxiliares
        cats_list = get_db_data(get_categories)
        ways_list = get_db_data(get_payment_methods)
        
        return {
            "fluxo": fluxo[0] if fluxo else {"vl_entradas": 0, "vl_saidas": 0, "custo_medio_mensal": 0, "saldo_atual": 0},
            "resumo": resumo,
            "gastos_categoria": categorias,
            "debitos_pendentes": debitos,
            "report_overview": report[0] if report else None,
            "categorias_lista": cats_list,
            "formas_pagamento_lista": ways_list
        }
    except Exception as e:
        logger.error(f"Erro no dashboard consolidado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visao-geral-relatorio/{ano}/{mes}")
def get_report_overview(ano: int, mes: int):
    periodo = (mes, ano)
    vl_total = get_db_data(fg_total_exp, periodo) or 0
    vl_pendente = get_db_data(fg_value_pending, (1, 0)) or 0
    qtd_pendente = get_db_data(fg_active_installments, (1, 0)) or 0
    
    return {
        "total_gastos": vl_total,
        "valor_disponivel": 7500 - vl_total,
        "valor_total_pendente": vl_pendente,
        "qtd_debitos_pendentes": qtd_pendente
    }

# --- BACKGROUND TASKS ---
def process_monthly_recurrences():
    try:
        recorrentes = get_recorrencias_ids()
        if not recorrentes: return
        
        db_res = database_connection()
        if not db_res: return
        conn, cursor = db_res
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # 1. Get descriptions already present in current month
        cursor.execute("SELECT LOWER(DESCRICAO) FROM TB_REG_FINANC WHERE MONTH(DATA_GASTO) = ? AND YEAR(DATA_GASTO) = ?", (current_month, current_year))
        descricoes_este_mes = {row[0] for row in cursor.fetchall()}
        
        # 2. Get details for recorrentes
        placeholders = ','.join(['?'] * len(recorrentes))
        query = f"SELECT DATA_GASTO, VALOR, DESCRICAO, LOCAL_GASTO, IDCATEGORIA, IDFORMA_PAGAMENTO, PARCELAMENTO, N_PARCELAS FROM TB_REG_FINANC WHERE ID_REGISTRO IN ({placeholders})"
        cursor.execute(query, recorrentes)
        targets = cursor.fetchall()
        
        for r in targets:
            dt_orig, valor, desc, local, cat_id, fp_id, parcelamento, n_parcelas = r
            if desc.lower() not in descricoes_este_mes:
                # Clone for current month
                dia = min(dt_orig.day, 28) if dt_orig else 1
                dt_nova = datetime(current_year, current_month, dia)
                
                array = {
                    "dt_registro": datetime.now(),
                    "dt_gasto": dt_nova.strftime('%Y-%m-%d'),
                    "valor": float(valor),
                    "desc": desc,
                    "desc_local": local,
                    "flag_parcelamento": parcelamento or "N",
                    "qt_parcelas": n_parcelas or 1,
                    "desc_categoria": cat_id,
                    "forma_pagamento": fp_id
                }
                
                # Check if IDs are names or actual IDs
                # record_financial expects IDs for cat and fp
                record_financial(array)
                descricoes_este_mes.add(desc.lower())

    except Exception as e:
        logger.error(f"Erro no processamento de recorrencias: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- ROTAS DE REGISTROS (CRUD) ---
@app.get("/api/transacoes")
def get_transactions(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_monthly_recurrences)
    query = with_no_filter()
    db_res = database_connection()
    if not db_res:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    conn, cursor = db_res
    try:
        recorrentes = get_recorrencias_ids()
        with conn:
            cursor.execute(query)
            rows = cursor.fetchall()
            return {"transacoes": [{
                "id": r[8], "dt_compra": r[0], "dt_pagamento": r[1], "total": r[2],
                "valor_parcela": r[3], "valor_pendente": r[4], "categoria": r[5],
                "descricao": r[6], "local": r[7], "forma_pagamento": r[9],
                "parcelamento": r[10], "n_parcelas": r[11],
                "recorrente": r[8] in recorrentes
            } for r in rows]}
    except Exception as e:
        logger.error(f"Erro ao buscar transações: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/transacoes")
def create_transaction(data: Dict[Any, Any] = Body(...)):
    try:
        data["dt_registro"] = datetime.now()
        record_financial(data)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Erro ao criar transação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/transacoes/{id_registro}")
def update_transaction(id_registro: int, data: Dict[Any, Any] = Body(...)):
    try:
        update_financial(data, id_registro)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Erro ao atualizar transação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from app.gui.services.file_generator import GenerateFile

@app.post("/api/exportar-relatorio")
def export_report_route(data: Dict[str, int] = Body(...)):
    try:
        mes = data.get("mes")
        ano = data.get("ano")
        if not mes or not ano:
            raise HTTPException(status_code=400, detail="Mês e ano são obrigatórios")
        
        generator = GenerateFile(mes_visualizacao=mes, ano_vizualizacao=ano)
        return {"status": "success", "path": str(generator.caminho_gerado)}
    except Exception as e:
        logger.error(f"Erro ao exportar relatório: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/transacoes/{id_registro}")
def delete_transaction(id_registro: int):
    try:
        deleta_item_treeview((id_registro,))
        # Tenta remover das recorrências também, se houver
        toggle_recorrencia_status(id_registro, False)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Erro ao deletar transação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transacoes/{id_registro}/recorrencia")
@app.post("/api/transacoes/{id_registro}/recorrencia/")
def update_recorrencia(id_registro: str, data: Dict[str, bool] = Body(...)):
    try:
        # Tenta converter para int se possível
        try:
            id_final = int(id_registro)
        except:
            id_final = id_registro
            
        status = data.get("recorrente", False)
        logger.info(f"Alterando recorrência do ID {id_final} para {status}")
        toggle_recorrencia_status(id_final, status)
        
        if status:
            process_monthly_recurrences()
        else:
            db_res = database_connection()
            if db_res:
                conn, cursor = db_res
                try:
                    cursor.execute("SELECT DESCRICAO FROM TB_REG_FINANC WHERE ID_REGISTRO = ?", (id_final,))
                    row = cursor.fetchone()
                    if row:
                        desc = row[0]
                        cursor.execute("DELETE FROM TB_REG_FINANC WHERE DESCRICAO = ? AND MONTH(DATA_GASTO) = ? AND YEAR(DATA_GASTO) = ? AND ID_REGISTRO != ?", (desc, datetime.now().month, datetime.now().year, id_final))
                        conn.commit()
                except Exception as e:
                    logger.error(f"Erro ao remover clone de recorrencia: {e}")
                finally:
                    cursor.close()
                    conn.close()
                    
        return {"status": "success", "recorrente": status}
    except Exception as e:
        logger.error(f"Erro ao atualizar recorrência: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)