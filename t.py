import urllib.request, urllib.parse, urllib.error
data = urllib.parse.urlencode({'username': 'teste@teste.com', 'password': '123'}).encode('utf-8')
req = urllib.request.Request(
    'https://troca-facil-backend.onrender.com/auth/login',
    data=data,
    method='POST',
    headers={'Origin': 'http://localhost:5173'}
)
try:
    res = urllib.request.urlopen(req)
    print("SUCESSO:", res.read().decode())
except urllib.error.HTTPError as e:
    body = e.read().decode()
    cors = e.headers.get('access-control-allow-origin', 'NÃO EXISTE')
    print(f"HTTP {e.code}")
    print(f"Body: {body}")
    print(f"CORS header: {cors}")
