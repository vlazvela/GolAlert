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

        return {"ligas": resumen[:1500]}  # Muestra solo las 50 primeras para empezar
    else:
        return f"❌ Error al obtener ligas: {response.status_code}"


from datetime import datetime
import json

@app.route('/init')
def filtrar_partidos_hoy():
    api_key = os.getenv("API_FOOTBALL_KEY")
    headers = { "x-apisports-key": api_key }

    # Fecha de hoy en formato YYYY-MM-DD
    hoy = datetime.utcnow().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={hoy}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"❌ Error al obtener partidos: {response.status_code}"

    # Cargar ligas permitidas desde el JSON
    with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
        ligas_permitidas = json.load(f)

    ids_permitidos = {liga["id"] for liga in ligas_permitidas}
    data = response.json()["response"]

    partidos_filtrados = []

    for partido in data:
        liga_id = partido["league"]["id"]
        if liga_id in ids_permitidos:
            partidos_filtrados.append({
                "liga": partido["league"]["name"],
                "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                "hora": partido["fixture"]["date"][11:16],
                "pais": partido["league"]["country"]
            })

    return {
        "fecha": hoy,
        "total_partidos": len(partidos_filtrados),
        "partidos": partidos_filtrados
    }


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)