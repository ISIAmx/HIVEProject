from flask import Flask
from flask import render_template
from db_operations import *
from flask import request, json, jsonify
from secrets import randbelow

from flaskext.mysql import MySQL  # Extension para accesar a Base de Datos

app = Flask(__name__)
mysql = MySQL()
app.config.from_object('config.DevConfig')  # Configuracion Desarrollador
mysql.init_app(app)

conn = mysql.connect()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/home_test', methods=['POST'])  # Registra Usuario
def insertarUsuario():
    json_data = request.get_json()

    username = json_data['username']
    password = json_data['password']

    registrado = existe_usuario(username, password)

    if registrado == True:
        status = 'Este usuario ya existe en Base de Datos'
        return json.dumps({'status': status})  # Devuleve Json
    else:
        # Inserta Usuario
        id = consultar_id()
        usr = (id, username, password)
        insert_user(conn, usr)
        status = 'Registrado con éxito'
        return json.dumps({'status': status})  # Devuleve Json


def existe_usuario(username, password):
    usuarios = query_users(conn)
    if usuarios == []:
        return False
    else:
        for usr in usuarios:
            if (username == usr['user']) & (password == usr['password']):
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


@app.route('/users')
def users():
    return render_template("users.html")


@app.route('/search_users')
def buscar_usuario():
    return render_template("search_user.html")


@app.route('/users', methods=['POST'])
def ver_usuarios():
    json_data = request.get_json()

    btn = json_data['click']

    if btn == 'true':
        users = query_users(conn)
        return (jsonify(users), 200)  # Devuleve Json


@app.route('/search_user', methods=['POST'])
def buscar_usuarios():
    opcion = ""
    json_data = request.get_json()
    if json_data['op'] == "1":
        opcion = "username"
        dato = json_data['nom']

    print(opcion)
    print(dato)

    users = query_data(conn, opcion, dato)
    print(users)
    return (jsonify(users), 200)  # Devuleve Json


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
