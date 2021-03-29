from flask import Flask
import flask
from flask import render_template, redirect, url_for, request
from flask import json, jsonify
from secrets import randbelow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow
from marshmallow import Schema
from hive.hive import Hive
from hive.blockchain import Blockchain
from lib import api
from lib import errorHandler
from sqlalchemy.sql import func


app = Flask(__name__)
app.config.from_object('config.DevConfig')  # Configuracion Desarrollador
db = SQLAlchemy(app)
ma = Marshmallow(app)


class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(200), nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    curator = db.Column(db.Boolean, nullable=False, default=False)


class upvotes(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    payout = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    vote_time = db.Column(db.DateTime, nullable=True)
    reward_sbd = db.Column(db.String(20), nullable=False)
    reward_sp = db.Column(db.String(20), nullable=False)


class test(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    created = db.Column(db.Date, nullable=False)
    last_update = db.Column(db.Date, nullable=False)
    net_votes = db.Column(db.Integer, nullable=False)
    pending_pv = db.Column(db.String(50), nullable=False)


class usersSchema(ma.Schema):
    class Meta:
        fields = ('id', 'account', 'hash', 'ip', 'created', 'admin', 'curator')


class testSchema(ma.Schema):
    class Meta:
        fields = ('id', 'author', 'title', 'created',
                  'last_update', 'net_votes', 'pending_pv')


class upvotesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'account', 'created', 'link',
                  'user', 'category', 'slug', 'title', 'type', 'payout', 'status', 'vote_time', 'reward_sbd', 'reward_sp')


# Para usar Flask-login
login_manager = LoginManager()
login_manager.login_view = 'app'
login_manager.init_app(app)

# Cargador de usuario


@login_manager.user_loader
def load_user(id):
    return users.query.get(int(id))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return render_template('home.html', profile=True)
    else:
        return render_template('home.html', profile=False)


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        username = json_data['username']
        password = json_data['password']
        userip = '0.0.0.0'

        # Nuevo usuario
        user = users.query.filter_by(account=username).first()
        if user:
            status = 'Bien! Usuario Existente'
            return json.dumps({'status': status})  # Devuleve Json
        else:
            # Insert new user
            new_user = users(account=username, hash=generate_password_hash(
                password, method='sha256'), ip=userip)
            db.session.add(new_user)
            db.session.commit()
            status = 'Registrado con éxito'
            return json.dumps({'status': status})  # Devuleve Json
    else:
        return render_template('register.html')


@ app.route('/login', methods=['GET', 'POST'])
def login():

    if flask.request.method == 'POST':
        json_data = request.get_json()
        username = json_data['username']
        userhash = json_data['userhash']

        user = users.query.filter_by(account=username).first()

        if not user or not check_password_hash(user.hash, userhash):
            status = '2'
            return json.dumps({'status': status})  # Devuleve Json
        else:
            login_user(user)
            status = '1'
            return json.dumps({'status': status})  # Devuleve Json
    else:
        return render_template('login.html')


@ app.route('/profile')
@ login_required
def profile():
    # check if user is an admin
    user = users.query.filter_by(account=current_user.account).first()

    if(user != None):
        return render_template('profile.html', username=current_user.account, admin_user=user.admin, curator_user=user.curator)
    else:
        return render_template('profile.html', username=current_user.account)


@ app.route('/profile_data')
@ login_required
def profile_dt():
    admin_schema = usersSchema(many=True)
    admin_table = users.query.all()
    json_data = admin_schema.dump(admin_table)
    print(json_data)
    return jsonify(json_data)


@ app.route('/delete_account', methods=['POST'])
@ login_required
def delete_account():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        id = json_data["id"]
        user_account = users.query.filter_by(id=id).one()
        db.session.delete(user_account)
        db.session.commit()
    return json.dumps({'success': True})


@ app.route('/update_account_status', methods=['POST'])
@ login_required
def update_account():
    if flask.request.method == 'POST':
        json_data = request.get_json()
        id = json_data["id"]
        option = json_data["option"]

        if(option == 1):
            cur = users.query.get(id)
            if(cur.curator == True):
                cur.curator = False
            else:
                cur.curator = True
        if(option == 2):
            dele = users.query.get(id)
            if(dele.delegator == True):
                dele.delegator = False
            else:
                dele.delegator = True
        if(option == 3):
            adm = users.query.get(id)
            if(adm.admin == True):
                adm.admin = False
            else:
                adm.admin = True

        db.session.commit()
        return json.dumps({'success': True})  # Devuleve Json


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin', methods=['POST'])
@login_required
def admin():
    hived_nodes = [
        'https://api.pharesim.me',
        'https://anyx.io',
        'https://api.hive.blog',
        'https://api.openhive.network',
    ]
    client = Hive(nodes=hived_nodes)
    # output variable
    data = {}
    # get and set variables
    username = None
    userhash = None
    deleteuv = None

    if 'username' in request.form:
        username = request.form['username']
    if 'userhash' in request.form:
        userhash = request.form['userhash']
    if 'deleteupvote' in request.form:
        deleteuv = request.form['deleteupvote']

    # check permissions
    users_schema = usersSchema()
    result = users.query.filter_by(account=username).first()
    result = users_schema.dump(result)

    if result['admin'] != True:
        return errorHandler.throwError('No permission')

    if deleteuv:
        upvotes_schema = upvotesSchema()
        result = upvotes.query.filter_by(id=deleteuv).first()
        result = upvotes_schema.dump(result)
        print(result)
        print("Antes de eliminacion")
        if result['status'] == 'in queue':
            print("Durante eliminacion")
            upvotes.query.filter_by(id=deleteuv).delete()
            db.session.commit()
            data['status'] = 'success'
            return data
        else:
            return errorHandler.throwError(
                'Only posts in queue can be removed from the queue. Duh!')
    else:
        # get upvotes
        upvotes_schema = upvotesSchema(many=True)
        upvote_table = upvotes.query.filter_by().order_by(upvotes.created.desc())
        dataJson = upvotes_schema.dump(upvote_table)
        data['upvotes'] = dataJson
        return data


@app.route('/upvote', methods=['POST'])
@login_required
def upvote():
    print("Upvote function")
    hived_nodes = [
        'https://api.pharesim.me',
        'https://anyx.io',
        'https://api.hive.blog',
        'https://api.openhive.network',
    ]

    user = "moo-cow"
    key = "5Jkmw272v8mF21RCWG6KveFyKJdXTsCc8w19uYgzLkmAUJB1XhE"
    client = Hive(keys=[key], nodes=hived_nodes)
    # output variable
    data = {}

    username = None
    userhash = None
    postlink = None
    deleteuv = None

    if 'username' in request.form:
        username = request.form['username']
    if 'deleteupvote' in request.form:
        deleteuv = request.form['deleteupvote']
    if 'postlink' in request.form:
        postlink = request.form['postlink']

    # check permissions
    users_schema = usersSchema()
    result = users.query.filter_by(account=username).first()
    result = users_schema.dump(result)

    if result['curator'] != True:
        return errorHandler.throwError('No permission')

    # delete post
    if deleteuv:
        upvotes_schema = upvotesSchema()
        posts = upvotes.query.filter_by(
            account=username, id=deleteuv).first()
        result = upvotes_schema.dump(posts)

        if len(result) < 1:
            return errorHandler.throwError('Upvote not found!')
        db.session.query(upvotes).filter(
            upvotes.id == deleteuv).update({'status': 'canceled'})
        db.session.commit()
        data['status'] = 'success'
        return data
    else:
        # submit new post
        if postlink:
            link = postlink.split('#')
            if len(link) > 1:
                link = link[1].split('/')
            else:
                link = postlink.split('/')
            post = client.get_content(link[-2][1:], link[-1])
            print(post)

            # check if curator is author himself
            if post['author'] == username:
                return errorHandler.throwError('Curating your own post? Are you serious?')

            # check if curator is author himself
            if post['author'] == 'curangel':
                return errorHandler.throwError('We do not vote for ourselves :D')

            # check if already voted
            for vote in post['active_votes']:
                if vote['voter'] == 'curangel':
                    return errorHandler.throwError('We already voted on that post.')

            # check if exists in upvote queue
            upvotes_schema = upvotesSchema()
            result = upvotes.query.filter_by(
                account=username, user=post['author'], slug=post['permlink']).first()
            result = upvotes_schema.dump(result)

            if len(result) > 0:
                return errorHandler.throwError(
                    'This post has been submitted before. Will not add to queue again.')

            post_type = 1
            if post['parent_author']:
                post_type = 2

            # insert upvote
            new_upvote = upvotes(account=username, link=post['url'], user=post['author'],
                                 category=post['category'], slug=post['permlink'], title=post['title'], type=post_type, payout=post['cashout_time'], status='in queue', reward_sbd=0, reward_sp=0)
            db.session.add(new_upvote)
            db.session.commit()

        # get upvotes
        upvotes_schema = upvotesSchema(many=True)
        upvote_table = upvotes.query.filter_by(
            account=username).order_by(upvotes.created.desc())
        dataJson = upvotes_schema.dump(upvote_table)

        # dataJson = jsonify(dataJson)
        data['upvotes'] = dataJson
        api.output(data)
        return data


if __name__ == '__main__':
    app.run(debug=True)
