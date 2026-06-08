import urllib.request, urllib.parse, urllib.error
data = urllib.parse.urlencode({'username': 'teste@teste.com', 'password': '123'}).encode('utf-8')
req = urllib.request.Request('https://troca-facil-backend.onrender.com/auth/login', data=data, method='POST')
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.read().decode())
