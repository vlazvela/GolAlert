# main.py version 1.2 - Listar solo partidos EN VIVO de nuestras ligas

import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv

# Cargar las variables de entorno desde .env
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# API Key desde variables de entorno
API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

print("API_KEY cargada:", bool(API_KEY))

# Endpoint para verificar conexión
@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

# Endpoint para listar partidos EN VIVO de ligas permitidas
@app.route('/live', methods=['GET'])
def partidos_en_vivo():
    try:
        # Cargar ligas permitidas
        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)
        ids_permitidos = {liga["id"] for liga in ligas_permitidas}

        # Llamada a fixtures en vivo
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        response = requests.get(url, headers=HEADERS)
        data = response.json().get("response", [])

        partidos_filtrados = []

        for partido in data:
            if partido["league"]["id"] in ids_permitidos:
                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                    "minuto": partido["fixture"]["status"]["elapsed"],
                    "marcador": f'{partido["goals"]["home"]} - {partido["goals"]["away"]}',
                    "pais": partido["league"]["country"]
                })

        return jsonify({
            "fecha": datetime.utcnow().strftime('%Y-%m-%d'),
            "total_partidos": len(partidos_filtrados),
            "partidos": partidos_filtrados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
