from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración de BD
DB_CONFIG = {
    'host': '185.232.14.52',
    'user': 'u760464709_22005123_usr',
    'password': 'LLK:CM#7Xi',
    'database': 'u760464709_22005123_bd',
    'charset': 'utf8mb4'
}

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None

# Crear tabla de rutinas
def create_tables():
    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rutinas (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        coach VARCHAR(255) NOT NULL,
                        descripcion TEXT NOT NULL,
                        efectividad DOUBLE NOT NULL
                    )
                ''')
            connection.commit()
            connection.close()
            print("Tabla 'rutinas' creada")
    except Exception as e:
        print(f"Error creando tabla: {e}")

@app.route('/')
def home():
    return "¡APP FUNCIONANDO! Módulo de Ivan Orlando"

@app.route('/rutinas')
def rutinas():
    return "Módulo de Rutinas - BD Configurada ✅"

@app.route('/test')
def test():
    return "✅ Test exitoso"

# Inicializar BD
with app.app_context():
    create_tables()

if __name__ == '__main__':
    app.run(debug=True)
