import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime, timedelta
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

# Endpoint raíz
@app.route('/')
def home():
    return "✅ GolAlert API en línea"

# Verificar conexión
@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

# Partidos de hoy (ajustado a hora Perú)
@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        hoy = datetime.utcnow().strftime('%Y-%m-%d')

        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        partidos_filtrados = []

        for liga in ligas_permitidas:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&date={hoy}"
            response = requests.get(url, headers=HEADERS)
            data = response.json()

            for partido in data.get("response", []):
                fecha_hora_utc = parser.isoparse(partido["fixture"]["date"])
                hora_local = (fecha_hora_utc - timedelta(hours=5)).strftime("%H:%M")

                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                    "hora": hora_local,
                    "pais": partido["league"]["country"]
                })

        return jsonify({
            "fecha": hoy,
            "total_partidos": len(partidos_filtrados),
            "partidos": partidos_filtrados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Estadísticas de partidos jugados ayer
@app.route('/estadisticas', methods=['GET'])
def obtener_estadisticas_partidos_finalizados():
    try:
        ayer = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        estadisticas = []

        for liga in ligas_permitidas:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&date={ayer}"
            res = requests.get(url, headers=HEADERS)
            data = res.json()

            for partido in data.get("response", []):
                if partido["fixture"]["status"]["short"] == "FT":
                    fixture_id = partido["fixture"]["id"]

                    stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
                    stats_res = requests.get(stats_url, headers=HEADERS)
                    stats_data = stats_res.json().get("response", [])

                    local = partido["teams"]["home"]["name"]
                    visitante = partido["teams"]["away"]["name"]
                    liga_nombre = partido["league"]["name"]
                    pais = partido["league"]["country"]

                    datos = {
                        "liga": liga_nombre,
                        "pais": pais,
                        "partido": f"{local} vs {visitante}",
                        "estadisticas": {}
                    }

                    for equipo in stats_data:
                        nombre_equipo = equipo["team"]["name"]
                        for stat in equipo["statistics"]:
                            tipo = stat["type"]
                            valor = stat["value"] or 0
                            clave = f"{tipo} ({nombre_equipo})"
                            datos["estadisticas"][clave] = valor

                    estadisticas.append(datos)

        return jsonify({
            "fecha": ayer,
            "total_partidos": len(estadisticas),
            "partidos": estadisticas
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)