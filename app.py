from flask import Flask, request, jsonify, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'clave_secreta_ivan'

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
    except Exception as e:
        print(f"Error creando tabla: {e}")

# LOGIN CON HTML INCLUIDO
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'pepe' and password == 'pepe':
            session['user'] = username
            return redirect(url_for('dashboard'))
    
    return '''
    <html>
    <body>
        <h2>Login - Ivan Orlando</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Usuario" value="pepe"><br>
            <input type="password" name="password" placeholder="Contraseña" value="pepe"><br>
            <button type="submit">Entrar</button>
        </form>
    </body>
    </html>
    '''

# DASHBOARD CON HTML INCLUIDO
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return '''
    <html>
    <body>
        <h1>Dashboard - ¡Bienvenido ''' + session['user'] + '''!</h1>
        <nav>
            <a href="/rutinas">Módulo de Rutinas</a> | 
            <a href="/logout">Cerrar Sesión</a>
        </nav>
    </body>
    </html>
    '''

# MÓDULO RUTINAS CON HTML INCLUIDO
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
                    cursor.execute("SELECT * FROM rutinas WHERE coach LIKE %s OR descripcion LIKE %s", (f'%{search}%', f'%{search}%'))
                else:
                    cursor.execute("SELECT * FROM rutinas")
                rutinas_list = cursor.fetchall()
            connection.close()
    except Exception as e:
        print(f"Error: {e}")
    
    # HTML COMPLETO DE RUTINAS
    html = f'''
    <html>
    <head>
        <title>Rutinas - Ivan Orlando</title>
        <style>
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Módulo de Rutinas</h1>
        <p>Usuario: {session['user']}</p>
        <a href="/dashboard">← Volver</a>
        
        <h3>Agregar Nueva Rutina</h3>
        <form id="formRutina">
            <input type="text" id="coach" placeholder="Coach" required>
            <input type="text" id="descripcion" placeholder="Descripción" required>
            <input type="number" id="efectividad" placeholder="Efectividad" step="0.1" required>
            <button type="submit">Agregar</button>
        </form>
        
        <h3>Buscar Rutinas</h3>
        <form method="GET">
            <input type="text" name="search" placeholder="Buscar..." value="{search}">
            <button type="submit">Buscar</button>
        </form>
        
        <h3>Rutinas Existentes</h3>
        {'<p>No hay rutinas registradas</p>' if not rutinas_list else '''
        <table>
            <tr><th>ID</th><th>Coach</th><th>Descripción</th><th>Efectividad</th><th>Acciones</th></tr>
            ''' + ''.join([f'''
            <tr>
                <td>{r['id']}</td>
                <td>{r['coach']}</td>
                <td>{r['descripcion']}</td>
                <td>{r['efectividad']}%</td>
                <td><button onclick="eliminarRutina({r['id']})">Eliminar</button></td>
            </tr>
            ''' for r in rutinas_list]) + '''
        </table>
        '''}
        
        <script>
            document.getElementById('formRutina').addEventListener('submit', function(e) {{
                e.preventDefault();
                const rutina = {{
                    coach: document.getElementById('coach').value,
                    descripcion: document.getElementById('descripcion').value,
                    efectividad: document.getElementById('efectividad').value
                }};
                
                fetch('/rutinas/agregar', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(rutina)
                }})
                .then(r => r.json())
                .then(data => {{
                    if(data.success) {{
                        alert('Rutina agregada');
                        location.reload();
                    }} else {{
                        alert('Error: ' + data.error);
                    }}
                }});
            }});
            
            function eliminarRutina(id) {{
                if(confirm('¿Eliminar rutina?')) {{
                    fetch('/rutinas/eliminar/' + id)
                        .then(r => r.json())
                        .then(data => {{
                            if(data.success) {{
                                alert('Rutina eliminada');
                                location.reload();
                            }} else {{
                                alert('Error: ' + data.error);
                            }}
                        }});
                }}
            }}
        </script>
    </body>
    </html>
    '''
    
    return html

# API RUTAS
@app.route('/rutinas/agregar', methods=['POST'])
def agregar_rutina():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'No autorizado'})
    
    try:
        data = request.get_json()
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO rutinas (coach, descripcion, efectividad) VALUES (%s, %s, %s)",
                    (data['coach'], data['descripcion'], float(data['efectividad']))
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
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM rutinas WHERE id = %s", (id,))
            connection.commit()
            connection.close()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# INICIALIZAR
with app.app_context():
    create_tables()

if __name__ == '__main__':
    app.run(debug=True)
