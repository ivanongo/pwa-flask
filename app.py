from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "¡APP FUNCIONANDO! Módulo de Ivan Orlando - Rutinas"

@app.route('/test')
def test():
    return "Ruta /test funcionando ✅"

@app.route('/rutinas')
def rutinas():
    return "Módulo de Rutinas funcionando ✅"

if __name__ == '__main__':
    app.run(debug=True)
