import requests # testando endpoints

headers = {
    "Authorization": "qualquercoisa12345"
}

req = requests.get("http://127.0.0.1:0000/auth/refresh", headers=headers)
print(req)
print(req.json())