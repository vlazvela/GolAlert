from flask import Flask

app = Flask(__name__)

@app.route('/run')
def ejecutar():
    return "✅ Script ejecutado correctamente desde Flask"

if __name__ == '__main__':
    app.run()
