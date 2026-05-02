import urllib.request
import json

url = "https://noncongruous-chiffonade-bernarda.ngrok-free.dev/api/transacoes/34/recorrencia"
data = json.dumps({"recorrente": True}).encode('utf-8')
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "pedro_financas_2026_seguro_!@"
}

req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
