import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime, timedelta
from dateutil import parser
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# API Key desde variable de entorno
API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

print("API_KEY cargada:", bool(API_KEY))

@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        # Fecha actual en hora Perú
        hoy_peru = datetime.utcnow() - timedelta(hours=5)
        fecha_actual = hoy_peru.date()

        # Cargar ligas permitidas
        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        partidos_filtrados = []

        # Consultamos 2 días (hoy y mañana en UTC) para no perder partidos del día en hora Perú
        fechas_consulta = [
            datetime.utcnow().strftime('%Y-%m-%d'),
            (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
        ]

        for liga in ligas_permitidas:
            for fecha in fechas_consulta:
                url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&date={fecha}"
                response = requests.get(url, headers=HEADERS)
                data = response.json()

                for partido in data.get("response", []):
                    # Convertir a hora Perú
                    hora_utc = parser.isoparse(partido["fixture"]["date"])
                    hora_peru = hora_utc - timedelta(hours=5)

                    # Filtrar solo si es del día actual en hora Perú
                    if hora_peru.date() == fecha_actual:
                        partidos_filtrados.append({
                            "liga": partido["league"]["name"],
                            "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                            "hora": hora_peru.strftime("%H:%M"),
                            "pais": partido["league"]["country"]
                        })

        return jsonify({
            "fecha": fecha_actual.strftime('%Y-%m-%d'),
            "total_partidos": len(partidos_filtrados),
            "partidos": partidos_filtrados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
