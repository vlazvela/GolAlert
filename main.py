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


#from datetime import timedelta

@app.route('/estadisticas', methods=['GET'])
def estadisticas_partidos():
    try:
        ayer = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        ids_ligas = {liga["id"] for liga in ligas_permitidas}
        partidos_con_estadisticas = []

        for liga_id in ids_ligas:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&date={ayer}"
            res = requests.get(url, headers=HEADERS)
            fixtures = res.json().get("response", [])

            for fixture in fixtures:
                match_id = fixture["fixture"]["id"]
                liga_nombre = fixture["league"]["name"]
                nombre_partido = f'{fixture["teams"]["home"]["name"]} vs {fixture["teams"]["away"]["name"]}'

                stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={match_id}"
                stats_res = requests.get(stats_url, headers=HEADERS)
                stats_data = stats_res.json().get("response", [])

                if len(stats_data) < 2:
                    continue

                local_stats = {item["type"]: item["value"] for item in stats_data[0]["statistics"]}
                visitante_stats = {item["type"]: item["value"] for item in stats_data[1]["statistics"]}

                tipos_deseados = [
                    "Goals", "Total Shots", "Shots on Goal", "Shots off Goal",
                    "Blocked Shots", "Corner Kicks", "Red Cards", "Saves",
                    "Big Chances", "Big Chances Missed"
                ]

                resumen = {}
                for tipo in tipos_deseados:
                    resumen[tipo] = {
                        "local": local_stats.get(tipo),
                        "visitante": visitante_stats.get(tipo)
                    }

                partidos_con_estadisticas.append({
                    "liga": liga_nombre,
                    "partido": nombre_partido,
                    "estadisticas": resumen
                })

        return jsonify({
            "fecha": ayer,
            "total_partidos": len(partidos_con_estadisticas),
            "partidos": partidos_con_estadisticas
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
