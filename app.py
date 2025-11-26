from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pymysql
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_pwa_ivan'

# Configuración de la base de datos - TUS CREDENCIALES
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

# Crear tabla de rutinas si no existe
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
            print("Tabla 'rutinas' creada/verificada correctamente")
    except Exception as e:
        print(f"Error creando tabla: {e}")

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'pepe' and password == 'pepe':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Credenciales incorrectas", 401
    
    return render_template('login.html')

# Ruta del dashboard
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# RUTAS PARA MÓDULO DE RUTINAS - TU TABLA
@app.route('/rutinas')
def rutinas():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    rutinas_list = []
    
    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                if search:
                    cursor.execute(
                        "SELECT * FROM rutinas WHERE coach LIKE %s OR descripcion LIKE %s",
                        (f'%{search}%', f'%{search}%')
                    )
                else:
                    cursor.execute("SELECT * FROM rutinas")
                rutinas_list = cursor.fetchall()
            connection.close()
    except Exception as e:
        print(f"Error: {e}")
    
    return render_template('rutinas.html', rutinas=rutinas_list, search=search)

@app.route('/rutinas/agregar', methods=['POST'])
def agregar_rutina():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        data = request.get_json()
        coach = data['coach']
        descripcion = data['descripcion']
        efectividad = float(data['efectividad'])
        
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO rutinas (coach, descripcion, efectividad) VALUES (%s, %s, %s)",
                    (coach, descripcion, efectividad)
                )
            connection.commit()
            connection.close()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Error de conexión'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/rutinas/eliminar/<int:id>')
def eliminar_rutina(id):
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM rutinas WHERE id = %s", (id,))
            connection.commit()
            connection.close()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Error de conexión'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Ruta para offline
@app.route('/offline')
def offline():
    return render_template('offline.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Ruta de prueba
@app.route('/test')
def test():
    return "✅ App funcionando - Módulo de Ivan Orlando"

# Inicializar tablas al inicio
with app.app_context():
    create_tables()

if __name__ == '__main__':
    app.run(debug=True)
