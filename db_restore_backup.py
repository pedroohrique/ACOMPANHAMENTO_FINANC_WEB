import pyodbc
import json
import time

def restore_database():
    path = r"app\database\connection_config.json"
    with open(path, 'r') as f:
        config = json.load(f)
    
    server = config["database"]["server"]
    db_name = config["database"]["name"]
    user = config["database"]["user"]
    password = config["database"]["password"]
    
    backup_path = r"C:\Temp\FINANCEIRO.bak"
    
    # Connecting to master to perform restore
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;UID={user};PWD={password};TrustServerCertificate=yes;'
    
    print(f"Iniciando restauracao do banco {db_name}...")
    
    try:
        # Use autocommit=True for administrative tasks like RESTORE
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # 1. Kick off users
        print("Setando modo SINGLE_USER...")
        cursor.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        
        # 2. Restore
        print(f"Restaurando de {backup_path}...")
        cursor.execute(f"RESTORE DATABASE [{db_name}] FROM DISK = '{backup_path}' WITH REPLACE")
        
        # 3. Set back to MULTI_USER
        print("Setando modo MULTI_USER...")
        cursor.execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER")
        
        cursor.close()
        conn.close()
        print("Restauracao concluida com sucesso!")
        
    except Exception as e:
        print(f"Erro na restauracao: {e}")
        # Try to set back to MULTI_USER just in case
        try:
            conn = pyodbc.connect(conn_str, autocommit=True)
            conn.cursor().execute(f"ALTER DATABASE [{db_name}] SET MULTI_USER")
        except:
            pass

if __name__ == "__main__":
    restore_database()
