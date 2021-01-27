from flask import Flask
import flask
from flask import render_template, redirect, url_for
from flask import request, json, jsonify
from secrets import randbelow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow
from marshmallow import Schema

app = Flask(__name__)
app.config.from_object('config.DevConfig')  # Configuracion Desarrollador
db = SQLAlchemy(app)
ma = Marshmallow(app)


class usuarios(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(100))


class admin(UserMixin, db.Model):
    id_admin = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(40))
    curator = db.Column(db.Boolean, unique=False, default=False)
    delegator = db.Column(db.Boolean, unique=False, default=False)
    admin = db.Column(db.Boolean, unique=False, default=False)
    created = db.Column(db.Date, default=date.today(), nullable=False)


class usuariosSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')


class adminSchema(ma.Schema):
    class Meta:
        fields = ('id_admin', 'account', 'curator',
                  'delegator', 'admin', 'created')


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
        else:
            # Crea nuevo usuario
            new_user = usuarios(username=username, password=generate_password_hash(
                password, method='sha256'))
            new_admin = admin(account=username)
            db.session.add(new_user)
            db.session.add(new_admin)
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
    # Verifing if user is an admin
    user = admin.query.filter_by(account=current_user.username).first()
    if(user != None):
        return render_template('profile.html', username=current_user.username, admin_user=user.admin)
    else:
        return render_template('profile.html', username=current_user.username)


@ app.route('/profile_data')
@login_required
def profile_dt():
    admin_schema = adminSchema(many=True)
    admin_table = admin.query.all()
    json_data = admin_schema.dump(admin_table)
    print(json_data)
    return jsonify(json_data)


@ app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        id = json_data["id_admin"]
        admin_account = admin.query.filter_by(id_admin=id).one()
        db.session.delete(admin_account)
        db.session.commit()
    return json.dumps({'success': True})  # Devuleve Json


@ app.route('/update_account_status', methods=['POST'])
@login_required
def update_account():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        id = json_data["id"]
        option = json_data["option"]

        if(option == 1):
            cur = admin.query.get(id)
            if(cur.curator == True):
                cur.curator = False
            else:
                cur.curator = True
        if(option == 2):
            dele = admin.query.get(id)
            if(dele.delegator == True):
                dele.delegator = False
            else:
                dele.delegator = True
        if(option == 3):
            adm = admin.query.get(id)
            if(adm.admin == True):
                adm.admin = False
            else:
                adm.admin = True
        db.session.commit()
        return json.dumps({'success': True})  # Devuleve Json


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

'''

if __name__ == '__main__':
    app.run(debug=True)
