import os
import requests
import json
from flask import Flask, jsonify
#from datetime import datetime
from datetime import datetime, timedelta
from dateutil import parser

# Inicializar Flask
app = Flask(__name__)

# API Key desde variables de entorno
API_KEY = os.getenv("API_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# Endpoint para verificar conexión
@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

# Endpoint para listar partidos de hoy en ligas permitidas
@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        #hoy = datetime.utcnow().strftime('%Y-%m-%d')
        #hoy = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
        #hoy = (datetime.utcnow() - timedelta(hours=5)).strftime('%Y-%m-%d')
        hoy = "2025-07-02"


        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        partidos_filtrados = []

        for liga in ligas_permitidas:
            #url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&season=2025&date={hoy}"
            url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&date={hoy}"
            response = requests.get(url, headers=HEADERS)
            data = response.json()

            for partido in data.get("response", []):
                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                    "hora": parser.isoparse(partido["fixture"]["date"]).strftime("%H:%M"),
                    "pais": partido["league"]["country"]
                })

        return jsonify({
            "mensaje": f"✅ {len(partidos_filtrados)} partidos encontrados",
            "partidos": partidos_filtrados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
