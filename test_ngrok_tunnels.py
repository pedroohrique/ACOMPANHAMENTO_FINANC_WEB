import urllib.request

try:
    with urllib.request.urlopen("http://localhost:4040/api/tunnels") as response:
        print(response.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
