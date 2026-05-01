import json
import pyodbc
from app.utils.logger import log_builder

log = log_builder("database.py")

_database_config = None

def _load_config():
    global _database_config
    if _database_config is not None:
        return _database_config
    path = r"app\database\connection_config.json"
    try:
        with open(path, 'r') as f:
            _database_config = json.load(f)
        return _database_config
    except FileNotFoundError:
        log.error(f"Arquivo de configuração não encontrado em: {path}")
        return None

def database_connection():
    database_config = _load_config()
    if not database_config:
        return None

    server = database_config["database"]["server"]
    database = database_config["database"]["name"]
    username = database_config["database"]["user"]
    password = database_config["database"]["password"]

    # Verificação rápida
    if not all([server, database, username, password]):
        log.error("Uma ou mais variáveis de ambiente do banco não foram carregadas.")
        return None

    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};DATABASE={database};'
            f'UID={username};PWD={password};'
            'TrustServerCertificate=yes;'
        )
        cursor = connection.cursor()
        return connection, cursor

    except pyodbc.Error as e:        
        log.error(f"Falha ao conectar ao banco de dados local: {e}")
        return None

