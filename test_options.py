import urllib.request

url = "http://localhost:8000/api/transacoes/34/recorrencia"
headers = {
    "X-API-Key": "pedro_financas_2026_seguro_!@"
}

req = urllib.request.Request(url, headers=headers, method="OPTIONS")

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
