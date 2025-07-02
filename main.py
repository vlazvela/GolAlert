from flask import Flask
import os

app = Flask(__name__)

@app.route('/run')
def ejecutar():
    return "✅ Script ejecutado correctamente desde Flask"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render usa una variable PORT
    app.run(host='0.0.0.0', port=port)        # Escucha desde cualquier IP
