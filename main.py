import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime, timedelta
from dateutil import parser
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# API Key desde .env
API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# Endpoint conexión
@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

# Endpoint para listar partidos del día actual (hora Perú)
@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        # Hoy en Perú
        hoy = (datetime.utcnow() - timedelta(hours=5)).strftime('%Y-%m-%d')

        # Cargar ligas permitidas
        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        partidos_filtrados = []

        for liga in ligas_permitidas:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&next=50"
            response = requests.get(url, headers=HEADERS)
            data = response.json()

            for partido in data.get("response", []):
                fecha_utc = parser.isoparse(partido["fixture"]["date"])
                hora_peru = fecha_utc - timedelta(hours=5)

                if hora_peru.strftime("%Y-%m-%d") == hoy:
                    partidos_filtrados.append({
                        "liga": partido["league"]["name"],
                        "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                        "hora": hora_peru.strftime("%H:%M"),
                        "pais": partido["league"]["country"]
                    })

        return jsonify({
            "fecha": hoy,
            "total_partidos": len(partidos_filtrados),
            "partidos": partidos_filtrados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
