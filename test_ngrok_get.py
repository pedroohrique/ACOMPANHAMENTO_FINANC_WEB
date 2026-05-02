import urllib.request

url = "https://noncongruous-chiffonade-bernarda.ngrok-free.dev/api/transacoes"
headers = {
    "X-API-Key": "pedro_financas_2026_seguro_!@"
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
