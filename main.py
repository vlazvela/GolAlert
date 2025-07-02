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


@app.route('/ligas')
def listar_ligas():
    api_key = os.getenv("API_FOOTBALL_KEY")
    url = "https://v3.football.api-sports.io/leagues"

    headers = {
        "x-apisports-key": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        ligas = response.json()["response"]
        resumen = []

        for liga in ligas:
            resumen.append({
                "id": liga["league"]["id"],
                "nombre": liga["league"]["name"],
                "pais": liga["country"]["name"],
                "temporada": liga["seasons"][-1]["year"]  # Última temporada disponible
            })

        return {"ligas": resumen[:700]}  # Muestra solo las 50 primeras para empezar
    else:
        return f"❌ Error al obtener ligas: {response.status_code}"


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
