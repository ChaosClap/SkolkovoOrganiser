import requests

server_ip = "http://<IP_СЕРВЕРА>:8000/status"  # Замени IP

try:
    response = requests.get(server_ip)
    if response.status_code == 200:
        print("Ответ от сервера:", response.json()["message"])
    else:
        print("Ошибка:", response.status_code)
except requests.exceptions.RequestException as e:
    print("Ошибка соединения:", e)
