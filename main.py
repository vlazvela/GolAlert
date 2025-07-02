
'''
from flask import Flask
import os

app = Flask(__name__)

@app.route('/run')
def ejecutar():
    return "✅ Script ejecutado correctamente desde Flask"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render usa una variable PORT
    app.run(host='0.0.0.0', port=port)        # Escucha desde cualquier IP
'''

from flask import Flask
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/run')
def ejecutar():
    api_key = os.getenv("API_FOOTBALL_KEY")
    if not api_key:
        return "❌ No se encontró la API key"

    url = "https://v3.football.api-sports.io/status"

    headers = {
        "x-apisports-key": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return f"✅ Conectado a API-Football: {response.json()['response']['account']['firstname']}"
    else:
        return f"❌ Error al conectar: {response.status_code} - {response.text}"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
