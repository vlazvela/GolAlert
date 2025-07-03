import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime, timedelta
from dateutil import parser

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        hoy = datetime.utcnow().strftime('%Y-%m-%d')

        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        partidos_filtrados = []

        for liga in ligas_permitidas:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&season={liga['temporada']}&date={hoy}"
            response = requests.get(url, headers=HEADERS)
            data = response.json()

            for partido in data.get("response", []):
                fecha_utc = parser.isoparse(partido["fixture"]["date"])
                hora_local = (fecha_utc - timedelta(hours=5)).strftime("%H:%M")

                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                    "hora": hora_local,
                    "pais": partido["league"]["country"]
                })

        return jsonify({
            "mensaje": f"✅ {len(partidos_filtrados)} partidos encontrados",
            "partidos": partidos_filtrados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
