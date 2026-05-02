import urllib.request
import json

url = "http://localhost:8000/api/v2/dashboard-full/2026/5"
req = urllib.request.Request(url, headers={"Authorization": "Bearer token_bypass"})
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print(f"Erro: {e}")
