from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pymysql
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_pwa_ivan'

# Configuración de la base de datos 
DB_CONFIG = {
    'host': '185.232.14.52',
    'user': 'u760464709_22005123_usr',
    'password': 'LLK:CM#7Xi',
    'database': 'u760464709_22005123_bd',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# Crear tabla de rutinas si no existe
def create_tables():
    try:
        connection = get_db_connection()
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
    except Exception as e:
        print(f"Error creando tabla: {e}")
    finally:
        connection.close()

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'pepe' and password == 'pepe':
            session['user'] = username
            return redirect(url_for('dashboard'))
    
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
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            if search:
                cursor.execute(
                    "SELECT * FROM rutinas WHERE coach LIKE %s OR descripcion LIKE %s",
                    (f'%{search}%', f'%{search}%')
                )
            else:
                cursor.execute("SELECT * FROM rutinas")
            rutinas = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        rutinas = []
    finally:
        connection.close()
    
    return render_template('rutinas.html', rutinas=rutinas, search=search)

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
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO rutinas (coach, descripcion, efectividad) VALUES (%s, %s, %s)",
                (coach, descripcion, efectividad)
            )
        connection.commit()
        connection.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/rutinas/eliminar/<int:id>')
def eliminar_rutina(id):
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM rutinas WHERE id = %s", (id,))
        connection.commit()
        connection.close()
        
        return jsonify({'success': True})
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

# Inicializar tablas al inicio
@app.before_first_request
def init_db():
    create_tables()

if __name__ == '__main__':
    app.run(debug=True)
