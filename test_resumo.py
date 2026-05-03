from app.database.querys import fg_monthly_summary
import json

def parse_currency(val):
    if val is None: return 0
    if isinstance(val, (int, float)): return float(val)
    try:
        s = str(val).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except: return 0

resumo_raw = fg_monthly_summary((2026,))
print("RAW:")
for r in resumo_raw:
    print(r)

print("\nPARSED:")
for l in resumo_raw:
    print({
        "mes": str(l[0]).strip(), "ano": l[1], "orcamento": parse_currency(l[2]),
        "gasto": parse_currency(l[3]), "saldo": parse_currency(l[4]),
        "percentual": l[5], "qtd": l[6], "maior_gasto": parse_currency(l[7]),
        "acumulado": parse_currency(l[8]), "variacao": parse_currency(l[9]), "percentual_var": l[10]
    })
