from fastapi import FastAPI, HTTPException, Body, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
from typing import Optional, Dict, Any
import json
import os
import jwt
from datetime import timedelta

# Configurações de Banco
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

RECORRENCIAS_FILE = os.path.join("app", "database", "recorrencias.json")
SECRET_KEY = "pedro_financas_2026_jwt_secret_key_super_segura"
ALGORITHM = "HS256"

app = FastAPI(title="API Acompanhamento Financeiro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _debug_log(hypothesis_id: str, location: str, message: str, data: Dict[str, Any], run_id: str = "pre-fix"):
    try:
        payload = {
            "sessionId": "496e72",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(datetime.now().timestamp() * 1000),
        }
        line = json.dumps(payload, ensure_ascii=False) + "\n"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, ".cursor", "debug-496e72.log"),
            os.path.join(base_dir, "debug-496e72.log"),
            os.path.join(os.getcwd(), "debug-496e72.log"),
            os.path.join(os.getcwd(), ".cursor", "debug-496e72.log"),
        ]
        for p in candidates:
            try:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "a", encoding="utf-8") as f:
                    f.write(line)
            except:
                pass
    except:
        pass

def get_recorrencias_ids():
    if not os.path.exists(RECORRENCIAS_FILE): return []
    try:
        with open(RECORRENCIAS_FILE, "r") as f: return json.load(f)
    except: return []

# Auxiliar para converter moeda
def parse_currency(val):
    if val is None: return 0
    if isinstance(val, (int, float)): return float(val)
    try:
        s = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except: return 0

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if (request.url.path.startswith("/api/auth") or request.method == "OPTIONS" or request.url.path == "/"):
        return await call_next(request)
    # Allow debug logging endpoint without auth (no secrets allowed in payload)
    if request.url.path == "/api/debug-log":
        return await call_next(request)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Não autenticado"})
    try:
        jwt.decode(auth_header.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        return await call_next(request)
    except:
        return JSONResponse(status_code=401, content={"detail": "Sessão inválida"})

@app.post("/api/debug-log")
async def debug_log_endpoint(payload: Dict[str, Any] = Body(...)):
    """
    Coleta logs do frontend (ngrok/https) e grava em arquivo local NDJSON.
    Não deve conter PII/segredos.
    """
    # #region agent log
    _debug_log(
        payload.get("hypothesisId", "FE"),
        "main_api.py:debug_log_endpoint",
        payload.get("message", "frontend log"),
        payload.get("data", {}),
        payload.get("runId", "pre-fix"),
    )
    # #endregion
    return {"ok": True}

@app.get("/api/v2/dashboard-full/{ano}/{mes}")
def get_dashboard_full(ano: int, mes: int):
    try:
        # #region agent log
        _debug_log(
            "H0",
            "main_api.py:get_dashboard_full",
            "request params received",
            {"ano": ano, "mes": mes},
        )
        # #endregion
        # Busca dados usando conexões individuais para garantir estabilidade (sem travar cursor)
        fluxo_raw = query_money_flow((mes, ano))
        resumo_raw = fg_monthly_summary((ano,))
        categorias_raw = fg_spent_by_category((mes, ano))
        debitos_raw = fg_outstanding_debts((0, 1))
        
        vl_total_mes = fg_total_exp((mes, ano)) or 0
        vl_pendente_total = fg_value_pending((1, 0)) or 0
        
        # Mapeamentos
        f = fluxo_raw[0] if fluxo_raw else [0, 0, 0, 0]
        categorias_map = category_map() or {}
        formas_map = payment_method_map() or {}
        # #region agent log
        _debug_log(
            "H1",
            "main_api.py:get_dashboard_full",
            "maps returned by DB layer (keys are labels?)",
            {
                "category_map_sample": list(categorias_map.items())[:5],
                "payment_method_map_sample": list(formas_map.items())[:5],
            },
        )
        # #endregion

        payload = {
            "fluxo": {
                "vl_entradas": float(f[0] or 0), "vl_saidas": float(f[1] or 0),
                "custo_medio_mensal": float(f[2] or 0), "saldo_atual": float(f[3] or 0)
            },
            "resumo": [{
                "mes": str(l[0]).strip(), "ano": l[1], "orcamento": parse_currency(l[2]),
                "gasto": parse_currency(l[3]), "saldo": parse_currency(l[4]),
                "percentual": l[5], "qtd": l[6], "maior_gasto": parse_currency(l[7]),
                "acumulado": parse_currency(l[8]), "variacao": parse_currency(l[9]), "percentual_var": l[10]
            } for l in (resumo_raw or [])],
            "gastos_categoria": [{"name": k, "value": float(v or 0)} for k, v in (categorias_raw or {}).items()],
            "debitos_pendentes": [{
                "id": d[8], # ID que estava faltando!
                "descricao": d[0], "mes_compra": d[1], "ano": d[2], "parcelas_pendentes": d[3],
                "valor_total": d[4], "valor_parcela": d[5], "valor_pendente": d[6],
                "mes_ultimo_debito": d[7], "ano_ultimo_debito": d[8]
            } for d in (debitos_raw or [])],
            "report_overview": {
                "total_gastos": float(vl_total_mes),
                "valor_disponivel": 7500.0 - float(vl_total_mes),
                "valor_total_pendente": float(vl_pendente_total)
            },
            "categorias_lista": [[k, v] for k, v in categorias_map.items()],
            "formas_pagamento_lista": [[k, v] for k, v in formas_map.items()]
        }
        # #region agent log
        _debug_log(
            "H1",
            "main_api.py:get_dashboard_full",
            "payload list samples (sent to frontend)",
            {
                "report_overview": payload.get("report_overview"),
                "fluxo": payload.get("fluxo"),
                "categorias_lista_sample": (payload.get("categorias_lista") or [])[:5],
                "formas_pagamento_lista_sample": (payload.get("formas_pagamento_lista") or [])[:5],
            },
        )
        # #endregion
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transacoes")
def get_transactions():
    try:
        query = with_no_filter()
        db_res = database_connection()
        conn, cursor = db_res
        cursor.execute(query)
        rows = cursor.fetchall()
        recorrentes = get_recorrencias_ids()
        res = []
        for r in rows:
            res.append({
                "id": r[8], "dt_compra": r[0], "dt_pagamento": r[1], "total": r[2],
                "valor_parcela": r[3], "valor_pendente": r[4], "categoria": r[5],
                "descricao": r[6], "local": r[7], "forma_pagamento": r[9],
                "parcelamento": r[10], "n_parcelas": r[11], "recorrente": r[8] in recorrentes
            })
        cursor.close()
        conn.close()
        return {"transacoes": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/transacoes/{id_registro}")
def delete_transaction(id_registro: int):
    try:
        deleta_item_treeview(id_registro)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transacoes")
def create_transaction(data: Dict[Any, Any] = Body(...)):
    data["dt_registro"] = datetime.now()
    record_financial(data)
    return {"status": "success"}

@app.put("/api/transacoes/{id_registro}")
def update_transaction(id_registro: int, data: Dict[Any, Any] = Body(...)):
    update_financial(data, id_registro)
    return {"status": "success"}

@app.post("/api/auth/login")
def login(data: Dict[str, str] = Body(...)):
    with open(os.path.join("app", "database", "users.json"), "r") as f:
        users = json.load(f)
    user = users.get(data.get("email"))
    if user and user["password"] == data.get("password"):
        token = jwt.encode({"sub": data["email"], "exp": datetime.utcnow() + timedelta(days=30)}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "user": {"nome": user["nome"], "email": data["email"]}}
    raise HTTPException(status_code=401, detail="Incorreto")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)