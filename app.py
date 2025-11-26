from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración simple de BD
DB_CONFIG = {
    'host': '185.232.14.52',
    'user': 'u760464709_22005123_usr',
    'password': 'LLK:CM#7Xi',
    'database': 'u760464709_22005123_bd'
}

@app.route('/')
def home():
    return "¡APP FUNCIONANDO! Módulo de Ivan Orlando"

@app.route('/login')
def login():
    return "Página de login"

@app.route('/rutinas')
def rutinas():
    return "Módulo de Rutinas - FUNCIONANDO"

@app.route('/test')
def test():
    return "✅ Test exitoso"

if __name__ == '__main__':
    app.run(debug=True)
