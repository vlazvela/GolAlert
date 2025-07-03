import os
import requests
import json
from flask import Flask, jsonify
from datetime import datetime, timedelta
from dateutil import parser
'''
import firebase_admin
from firebase_admin import credentials, firestore
'''
# Inicializar Flask
app = Flask(__name__)
'''
# Inicializar Firebase
cred = credentials.Certificate("clave-firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
'''
# Variables globales
API_KEY = os.getenv("API_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# Función para filtrar partidos de hoy en las ligas permitidas
@app.route('/init', methods=['GET'])
def filtrar_partidos_hoy():
    try:
        hoy = datetime.utcnow().strftime('%Y-%m-%d')

        # Leer archivo de ligas permitidas
        with open("ligas_permitidas.json", "r", encoding="utf-8") as f:
            ligas_permitidas = json.load(f)

        ligas_ids = [liga["id"] for liga in ligas_permitidas]
        partidos_filtrados = []

        for liga in ligas_permitidas:
            url = f"https://v3.football.api-sports.io/fixtures?league={liga['id']}&season={liga['temporada']}&date={hoy}"
            response = requests.get(url, headers=HEADERS)
            data = response.json()

            for partido in data.get("response", []):
                fecha_utc = parser.isoparse(partido["fixture"]["date"])
                hora_local = (fecha_utc - timedelta(hours=5)).strftime("%H:%M")  # UTC-5 para Perú

                partidos_filtrados.append({
                    "liga": partido["league"]["name"],
                    "partido": f'{partido["teams"]["home"]["name"]} vs {partido["teams"]["away"]["name"]}',
                    "hora": hora_local,
                    "pais": partido["league"]["country"]
                })

        return jsonify({"mensaje": f"✅ {len(partidos_filtrados)} partidos guardados para hoy"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Conexión simple para probar la API
@app.route('/run')
def index():
    return "✅ Conectado a API-Football: Vlaz"

# Ejecución
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


'''
        # Guardar en Firebase
        doc_ref = db.collection("partidos").document("hoy")
        doc_ref.set({
            "fecha": hoy,
            "partidos": partidos_filtrados
        })
'''