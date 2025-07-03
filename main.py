import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        hoy = datetime.utcnow().strftime('%Y-%m-%d')
        url = f"https://v3.football.api-sports.io/fixtures?date={hoy}"

        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return jsonify({"error": f"❌ Error al obtener partidos: {response.status_code}"}), 500

        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        ids_permitidos = {liga["id"] for liga in ligas_permitidas}
        data = response.json().get("response", [])

        partidos_filtrados = []

        for partido in data:
            liga_id = partido["league"]["id"]
            if liga_id in ids_permitidos:
                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                    "hora": partido["fixture"]["date"][11:16],  # solo hora HH:MM
                    "pais": partido["league"]["country"]
                })

        return jsonify({
            "fecha": hoy,
            "total_partidos": len(partidos_filtrados),
            "partidos": partidos_filtrados
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
