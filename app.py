from flask import Flask
import flask
from flask import render_template
from db_operations import *
from flask import request, json, jsonify
from secrets import randbelow
# Libreria para generar hash
from werkzeug.security import generate_password_hash, check_password_hash

from flaskext.mysql import MySQL  # Extension para accesar a Base de Datos

app = Flask(__name__)
mysql = MySQL()
app.config.from_object('config.DevConfig')  # Configuracion Desarrollador
mysql.init_app(app)

conn = mysql.connect()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        username = json_data['username']
        password = json_data['password']

        hashed_password = generate_password_hash(password)

        registrado = existe_usuario(username, hashed_password)

        if registrado == True:
            status = 'Este usuario ya existe, intente con otro'
            return json.dumps({'status': status})  # Devuleve Json
        else:
            # Inserta Usuario
            id = consultar_id()
            usr = (id, username, hashed_password)
            insert_user(conn, usr)
            status = 'Registrado con éxito'
            return json.dumps({'status': status})  # Devuleve Json
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        username = json_data['username']
        password = json_data['password']

        registrado = existe_usuario(username, password)

        if registrado == True:
            status = 'Bienvenido'
        else:
            status = 'Usuario Inexistente'
        return json.dumps({'status': status})  # Devuleve Json
    else:
        return render_template('login.html')


def existe_usuario(username, pwd):
    usuarios = query_users(conn)

    if usuarios == []:
        return False
    else:
        for usr in usuarios:
            if (username == usr['user']) or (check_password_hash(usr['password'], pwd)):
                return True

        return False


def consultar_id():
    while True:
        id = randbelow(10000)
        usuarios = query_users(conn)
        if usuarios == []:
            return id
        else:
            for usr in usuarios:
                if id != usr['id']:
                    return id


@app.route('/delete_user', methods=['POST'])
def borrar_usuarios():

    json_data = request.get_json()
    id_borrar = json_data["id"]

    delete_user(conn, id_borrar)
    status = "Usuario Eliminado de Base de Datos"
    return json.dumps({'status': status})  # Devuleve Json


@app.route('/update_user', methods=['POST'])
def update_user():

    json_data = request.get_json()

    id = json_data['id']
    nom = json_data['nom']
    password = json_data['con']

    # Modifica Usuario
    usr = (nom, password, id)
    update_usr(conn, usr)
    status = 'Modificado con éxito'
    return json.dumps({'status': status})  # Devuleve Json


if __name__ == '__main__':
    app.run(debug=True)
