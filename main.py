import os
import requests
import json
from flask import Flask, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-apisports-key": API_KEY
}

print("API_KEY cargada:", bool(API_KEY))

@app.route('/test-live', methods=['GET'])
def partidos_en_vivo():
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        partidos = []

        for partido in data.get("response", []):
            fixture_id = partido["fixture"]["id"]
            minuto = partido["fixture"]["status"]["elapsed"] or 0
            local = partido["teams"]["home"]["name"]
            visitante = partido["teams"]["away"]["name"]
            goles_local = partido["goals"]["home"]
            goles_visitante = partido["goals"]["away"]
            liga = partido["league"]["name"]
            pais = partido["league"]["country"]

            # Obtener estadísticas del fixture
            stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
            stats_res = requests.get(stats_url, headers=HEADERS)
            stats_data = stats_res.json().get("response", [])

            estadisticas_filtradas = {}
            tipos_deseados = [
                "Total Shots", "Shots on Goal", "Shots off Goal", "Blocked Shots",
                "Corner Kicks", "Red Cards", "Goalkeeper Saves",
                "Big Chances", "Big Chances Missed"
            ]

            for equipo in stats_data:
                nombre_equipo = equipo["team"]["name"]
                for stat in equipo["statistics"]:
                    tipo = stat["type"]
                    valor = stat["value"] or 0
                    if tipo in tipos_deseados:
                        clave = f"{tipo} ({nombre_equipo})"
                        estadisticas_filtradas[clave] = valor

            partidos.append({
                "liga": liga,
                "pais": pais,
                "fixture_id": partido["fixture"]["id"],
                "partido": f"{local} vs {visitante}",
                "minuto": minuto,
                "marcador": f"{goles_local} - {goles_visitante}",
                "estadisticas": estadisticas_filtradas
            })

        return jsonify({
            "total_partidos": len(partidos),
            "partidos": partidos
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
