# 🔧 list_usa_leagues versión 1 — list_usa_leagues.py
# 📝 Sirve para obtener IDs reales desde la API

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

print("🔄 Consultando ligas de USA...")
resp = requests.get("https://v3.football.api-sports.io/leagues?country=USA", headers=HEADERS)

print("Status:", resp.status_code)
for item in resp.json().get("response", []):
    league = item["league"]
    print(f"{league['id']} — {league['name']} ({item['country']['name']})")
