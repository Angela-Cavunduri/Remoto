import urllib.request, urllib.error
req = urllib.request.Request('https://troca-facil-backend.onrender.com/usuarios/')
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.read().decode())
