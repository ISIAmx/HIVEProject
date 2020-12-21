from flask import Flask
import flask
from flask import render_template, redirect, url_for
#from db_operations import *
from flask import request, json, jsonify
from secrets import randbelow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DevConfig')  # Configuracion Desarrollador
db = SQLAlchemy(app)


class usuarios(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(100))


# Para usar Flask-login
login_manager = LoginManager()
login_manager.login_view = 'app'
login_manager.init_app(app)


# Cargador de usuario
@login_manager.user_loader
def load_user(user_id):
    return usuarios.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        username = json_data['username']
        password = json_data['password']

        user = usuarios.query.filter_by(username=username).first()

        if user:  # Si el usuario existe
            status = 'Bien! Usuario Existente'
            return json.dumps({'status': status})  # Devuleve Json
        # Crea nuevo usuario
        new_user = usuarios(username=username, password=generate_password_hash(
            password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()
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

        user = usuarios.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            status = '2'
            return json.dumps({'status': status})  # Devuleve Json
        else:
            login_user(user)
            status = '1'
            return json.dumps({'status': status})  # Devuleve Json
    else:
        return render_template('login.html')


@ app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


'''
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


@ app.route('/delete_user', methods=['POST'])
def borrar_usuarios():

    json_data = request.get_json()
    id_borrar = json_data["id"]

    delete_user(conn, id_borrar)
    status = "Usuario Eliminado de Base de Datos"
    return json.dumps({'status': status})  # Devuleve Json


@ app.route('/update_user', methods=['POST'])
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
'''

if __name__ == '__main__':
    app.run(debug=True)
