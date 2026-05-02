from app.database.querys import query_money_flow
from app.database.connection import database_connection

res = query_money_flow((5, 2026))
print(f"Tipo: {type(res[0])}")
print(f"Conteudo: {res[0]}")
try:
    print(f"AsDict: {res[0].__dict__}")
except:
    print("No __dict__")
