import requests

# Testando localmente (considerando que o servidor está rodando na porta 8000)
url = "http://localhost:8000/api/v2/dashboard-full/2026/5"
# Note: No headers for now because I made it lenient
try:
    response = requests.get(url, headers={"Authorization": "Bearer token_bypass"})
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(f"Erro: {e}")
