import os
import requests
import json
from flask import Flask, jsonify
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración inicial
app = Flask(__name__)
API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# Endpoint para mostrar partidos EN VIVO de ligas permitidas
@app.route('/live', methods=['GET'])
def partidos_en_vivo():
    try:
        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        ids_permitidos = {liga["id"] for liga in ligas_permitidas}
        url = "https://v3.football.api-sports.io/fixtures?live=all"

        response = requests.get(url, headers=HEADERS)
        data = response.json()

        partidos_filtrados = []

        for partido in data.get("response", []):
            liga_id = partido["league"]["id"]
            if liga_id in ids_permitidos:
                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "pais": partido["league"]["country"],
                    "partido": f"{partido['teams']['home']['name']} vs {partido['teams']['away']['name']}",
                    "minuto": partido["fixture"]["status"]["elapsed"],
                    "resultado": f"{partido['goals']['home']} - {partido['goals']['away']}"
                })

        return jsonify({
            "total_partidos_en_vivo": len(partidos_filtrados),
            "partidos": partidos_filtrados
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Verificación de conexión
@app.route('/run')
def index():
    return "✅ API-Football conectada"

# Ejecutar app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)