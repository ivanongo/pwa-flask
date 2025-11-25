# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt
# Módulo de Ivan Orlando - Rutinas

from functools import wraps
from flask import Flask, render_template, request, jsonify, make_response, session

from flask_cors import CORS, cross_origin

import mysql.connector.pooling
import pusher
import pytz
import datetime

app            = Flask(__name__)
app.secret_key = "Test12345"
CORS(app)
con_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    host="185.232.14.52",
    database="u760464709_prueba_bd",
    user="u760464709_prueba_usr",
    password="FnlRDqu3@A"
)


@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")

@app.route("/pwa-sw.js")
def pwaSW():
    return app.send_static_file("pwa-sw.js")


def pusherModulo():
    pusher_client = pusher.Pusher()
    
    pusher_client.trigger("canalModulos", "eventoModulo", {})
    return make_response(jsonify({}))

def login(fun):
    @wraps(fun)
    def decorador(*args, **kwargs):
        if not session.get("login2"):
            return jsonify({
                "estado": "error",
                "respuesta": "No has iniciado sesión"
            }), 401
        return fun(*args, **kwargs)
    return decorador


@app.route("/")
def landingPage():
    return render_template("landing-page.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def appLogin():
    return render_template("login.html")
    # return "<h5>Hola, soy la view app</h5>"

@app.route("/registros")
def registros():
    return render_template("registros.html")

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/notificaciones")
def notificaciones():
    return render_template("notificaciones.html")

@app.route("/offline")
def offline():
    return render_template("offline.html")


@app.route("/ping")
def ping():
    return "ping"

@app.route("/fechaHora")
def fechaHora():
    tz    = pytz.timezone("America/Matamoros")
    ahora = datetime.datetime.now(tz)
    return ahora.strftime("%Y-%m-%d %H:%M:%S")

@app.route("/iniciarSesion", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def iniciarSesion():
    usuario    = request.form["usuario"]
    contrasena = request.form["contrasena"]

    con    = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT id, usuario
    FROM usuarios
    WHERE usuario  = %s
    AND contrasena = %s
    """
    val    = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    session["login2"]     = False
    session["login2-id"]  = None
    session["login2-usr"] = None
    if registros:
        usuario = registros[0]
        session["login2"]     = True
        session["login2-id"]  = usuario["id"]
        session["login2-usr"] = usuario["usuario"]

    return make_response(jsonify(registros))

@app.route("/cerrarSesion", methods=["POST"])
@login
def cerrarSesion():
    session["login2"]     = False
    session["login2-id"]  = None
    session["login2-usr"] = None
    return make_response(jsonify({}))

@app.route("/preferencias")
@login
def preferencias():
    return make_response(jsonify({
        "usr": session.get("login2-usr")
    }))


@app.route("/registros/buscar", methods=["GET"])
@login
def buscarRegistros():
    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"

    try:
        con    = con_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        sql    = """
        SELECT id,
            descripcion,
            fechaHora
        FROM registros
        WHERE descripcion LIKE %s
        ORDER BY id DESC
        LIMIT 25 OFFSET 0
        """
        val    = (busqueda, )

        cursor.execute(sql, val)
        registros = cursor.fetchall()

    except mysql.connector.errors.ProgrammingError as error:
        registros = []

    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()

    return make_response(jsonify(registros))

@app.route("/registro/guardar", methods=["POST"])
@login
def guardarRegistro():
    id          = request.form["id"]
    descripcion = request.form["descripcion"]
    tz          = pytz.timezone("America/Matamoros")
    ahora       = datetime.datetime.now(tz)
    fechaHora   = ahora.strftime("%Y-%m-%d %H:%M:%S")

    con    = con_pool.get_connection()
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE registros
        SET descripcion = %s
        WHERE id = %s
        """
        val = (descripcion, id)
    else:
        sql = """
        INSERT INTO registros (descripcion, fechaHora)
        VALUES                (%s,          %s)
        """
        val =                 (descripcion, fechaHora)
    
    cursor.execute(sql, val)
    con.commit()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    lastInsertId = id
    if not id:
        lastInsertId = cursor.lastrowid

    return make_response(jsonify({
        "id": lastInsertId,
        "fechaHora": fechaHora
    }))

@app.route("/registro/<int:id>")
@login
def editarRegistro(id):
    con    = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT id, descripcion, fechaHora
    FROM registros
    WHERE id = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    return make_response(jsonify(registros))

@app.route("/registro/eliminar", methods=["POST"])
def eliminarRegistro():
    id = request.form["id"]

    con    = con_pool.get_connection()
    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM registros
    WHERE id = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    if cursor:
        cursor.close()
    if con and con.is_connected():
        con.close()

    return make_response(jsonify({}))


@app.route("/notificaciones/cargar", methods=["GET"])
@login
def cargarNotificaciones():
    # args     = request.args
    # busqueda = args["busqueda"]
    # busqueda = f"%{busqueda}%"

    try:
        con    = con_pool.get_connection()
        cursor = con.cursor(dictionary=True)
        sql    = """
        SELECT id,
            titulo,
            contenido,
            fechaHora,
            `READ`
        FROM notificaciones
        WHERE notificaciones.usuario = %s
        ORDER BY id DESC
        LIMIT 25 OFFSET 0
        """
        val    = (session.get("login2-id"), )

        cursor.execute(sql, val)
        registros = cursor.fetchall()

    except mysql.connector.errors.ProgrammingError as error:
        registros = []

    finally:
        if cursor:
            cursor.close()
        if con and con.is_connected():
            con.close()

    return make_response(jsonify(registros))

@app.route("/notificacion/eliminar", methods=["POST"])
@login
def eliminarNotificacion():
    return "eliminar"

@app.route("/notificacion/marcarComoLeida", methods=["POST"])
@login
def marcarNotificacionComoLeida():
    return "leida"

if __name__ == "__main__":
    app.run()
