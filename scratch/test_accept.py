import requests

url = "https://troca-facil-backend.onrender.com/trocas/1/aceitar"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNCIsImV4cCI6MTc4MTgxMjY2NX0.YFpwxgeo5HeW07f-6M-FhrqkKuF8NluXzQ4BtafQmo4"
}

response = requests.put(url, headers=headers)
print("Status code:", response.status_code)
print("Response body:", response.text)
