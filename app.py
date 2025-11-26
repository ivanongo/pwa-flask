from flask import Flask, render_template, request, jsonify, redirect, url_for, session
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

# Ruta de login CON FORMULARIO HTML
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'pepe' and password == 'pepe':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Credenciales incorrectas. Usa: pepe/pepe"
    
    # FORMULARIO HTML para login
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
    </head>
    <body>
        <h2>Login - Módulo de Ivan Orlando</h2>
        <form method="POST">
            <p>Usuario: <input type="text" name="username" value="pepe"></p>
            <p>Contraseña: <input type="password" name="password" value="pepe"></p>
            <button type="submit">Entrar</button>
        </form>
        <p><strong>Usa:</strong> pepe / pepe</p>
    </body>
    </html>
    '''

# Dashboard
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return '''
    <h1>Dashboard - ¡Bienvenido!</h1>
    <p>Usuario: ''' + session['user'] + '''</p>
    <p><a href="/rutinas">Ir a Módulo de Rutinas</a></p>
    <p><a href="/logout">Cerrar Sesión</a></p>
    '''

# Módulo de Rutinas
@app.route('/rutinas')
def rutinas():
    if 'user' not in session:
        return redirect(url_for('login'))
    return '''
    <h1>Módulo de Rutinas</h1>
    <p>¡Funcionando correctamente! ✅</p>
    <p>Usuario: ''' + session['user'] + '''</p>
    <p><a href="/dashboard">Volver al Dashboard</a></p>
    '''

@app.route('/test')
def test():
    return "✅ Test exitoso"

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Inicializar BD
with app.app_context():
    create_tables()

if __name__ == '__main__':
    app.run(debug=True)
