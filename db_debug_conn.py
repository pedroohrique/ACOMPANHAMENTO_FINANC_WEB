?import pyodbc
import json

path = r"app\database\connection_config.json"
with open(path, 'r') as f:
    config = json.load(f)

server = config["database"]["server"]
database = config["database"]["name"]
username = config["database"]["user"]
password = config["database"]["password"]

try:
    print(f"Tentando conectar ao server={server}, db={database}...")
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={server};DATABASE={database};'
        f'UID={username};PWD={password};'
        'TrustServerCertificate=yes;'
    )
    print("Conexao Driver 17 OK!")
except Exception as e1:
    print(f"Erro Driver 17: {e1}")
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            f'SERVER={server};DATABASE={database};'
            f'UID={username};PWD={password};'
            'TrustServerCertificate=yes;'
        )
        print("Conexao Driver 18 OK!")
    except Exception as e2:
        print(f"Erro Driver 18: {e2}")
