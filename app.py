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
from hive.account import Account
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


class blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    account = db.Column(db.String(100), nullable=False)


class upvotes(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    payout = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    vote_time = db.Column(db.DateTime, nullable=True)
    reward_sbd = db.Column(db.String(20), nullable=False)
    reward_sp = db.Column(db.String(20), nullable=False)


class downvotes(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    payout = db.Column(db.DateTime, nullable=False)
    reward = db.Column(db.Integer, nullable=False)
    maxi = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)


class usersSchema(ma.Schema):
    class Meta:
        fields = ('id', 'account', 'hash', 'ip', 'created', 'admin', 'curator')


class upvotesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'account', 'created', 'link',
                  'user', 'category', 'slug', 'title', 'type', 'payout', 'status', 'vote_time', 'reward_sbd', 'reward_sp')


class blacklistSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user', 'reason', 'created', 'account')


class downvotesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'account', 'created', 'reason', 'link',
                  'user', 'category', 'slug', 'title', 'type', 'payout', 'reward', 'maxi', 'status')


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        username = None
        userhash = None

        if 'username' in request.form:
            username = request.form['username']
        if 'userhash' in request.form:
            userhash = request.form['userhash']
        userip = '0.0.0.0'

        # save a new entry
        if username and userhash:
            # check if user exists
            user = users.query.filter_by(account=username).first()
            if user:
                # Devuleve Json
                return errorHandler.throwError("User already registered")
            else:
                # Write
                new_user = users(account=username, hash=generate_password_hash(
                    userhash, method='sha256'), ip=userip)
                # new_user = users(account=username, hash=generate_password_hash(
                #    userhash, method='sha256'), ip=userip)
                db.session.add(new_user)
                db.session.commit()
                return json.dumps({'status': 'success'})  # Devuleve Json
        else:
            errorHandler.throwError("Unsufficient userdata to register")


@ app.route('/login', methods=['GET', 'POST'])
def login():
    hived_nodes = [
        'https://api.pharesim.me',
        'https://anyx.io',
        'https://api.hive.blog',
        'https://api.openhive.network',
    ]

    client = Hive(nodes=hived_nodes)
    # output variable
    user = {}

    # get and set variables
    username = None
    userhash = None
    if 'username' in request.form:
        username = request.form['username']
    if 'userhash' in request.form:
        userhash = request.form['userhash']
    print(userhash)
    # check user exists
    users_schema = usersSchema()
    results = users.query.filter_by(account=username).first()
    results = users_schema.dump(results)
    print(results)

    # if not user or not check_password_hash(user.hash, userhash):
    #       status = '2'
    #       return json.dumps({'status': status})  # Devuleve Json

    if len(results) > 0:
        # if results['hash'] == userhash:
        if check_password_hash(results['hash'], userhash):
            user['account'] = username
            user['admin'] = results['admin']
            user['curator'] = results['curator']
            user['delegator'] = 0

            delegations = client.get_vesting_delegations(
                username, 'curangel', 1)
            if len(delegations) > 0 and delegations[0]['delegatee'] == 'curangel':
                user['delegator'] = 1
            print(user)
            return user
        else:
            return errorHandler.throwError('Login failed')
    else:
        return errorHandler.throwError('Unknown user')


@app.route('/admin', methods=['GET', 'POST'])
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
    switch = None
    blackl = None
    reason = None
    deletebl = None

    # Schemas

    upvotes_schema = upvotesSchema(many=True)
    blacklist_schema = blacklistSchema(many=True)
    downvotes_schema = downvotesSchema(many=True)
    # Schemas

    if 'username' in request.form:
        username = request.form['username']
    if 'userhash' in request.form:
        userhash = request.form['userhash']
    if 'deleteupvote' in request.form:
        deleteuv = request.form['deleteupvote']
    if 'deletedownvote' in request.form:
        deletedv = request.form['deletedownvote']
    if 'switch' in request.form:
        switch = request.form['switch']
    if 'account' in request.form:
        account = request.form['account']
    if 'blacklist' in request.form:
        blackl = request.form['blacklist']
    if 'reason' in request.form:
        reason = request.form['reason']
    if 'deleteBlacklist' in request.form:
        deletebl = request.form['deleteBlacklist']

    # check permissions
    users_schema = usersSchema()
    result = users.query.filter_by(account=username).first()
    result = users_schema.dump(result)

    if result['admin'] != True:
        return errorHandler.throwError('No permission')

    if switch:
        if switch == 'admin' or switch == 'delete':
            users_table = users.query.filter_by(
                admin=True).order_by(users.id.desc())
            results = users_schema.dump(users_table)
            if len(results) < 2:
                errorHandler.throwError('There has to be one admin')
        if switch == 'delete':
            users.query.filter_by(id=account).delete()
            db.session.commit()
        else:
            users_table = users.query.filter_by(id=account).first()
            results = users_schema.dump(users_table)
            if results[switch] == 1:
                new = 0
            else:
                new = 1
            db.session.query(users).filter(
                users.id == account).update({switch: new})
            db.session.commit()
        data['status'] = 'success'

    elif deleteuv:
        result = upvotes.query.filter_by(id=deleteuv).first()
        result = upvotes_schema.dump(result)
        if result['status'] == 'in queue':
            upvotes.query.filter_by(id=deleteuv).delete()
            db.session.commit()
            data['status'] = 'success'
        else:
            return errorHandler.throwError(
                'Only posts in queue can be removed from the queue. Duh!')
    elif blackl:
        if reason:
            bl = blacklist.query.filter_by(user=blackl).first()
            bl = blacklist_schema.dump(bl)
            if len(bl) > 0:
                return errorHandler.throwError('User is already blacklisted.')
            newbl = blacklist(user=blackl, reason=reason, account=username)
            db.session.add(newbl)
            db.session.commit()
            data['status'] = 'success'
        else:
            return errorHandler.throwError('You need to give a reason to blacklisting')
    elif deletebl:
        blacklist.query.filter_by(id=deletebl).delete()
        db.session.commit()
        data['status'] = 'success'

    elif deletedv:
        downvotes_schema = downvotes_schema()
        post = downvotes.query.filter_by(id=deletedv).first()
        post = downvotes_schema.dump(post)
        if (post['status'] == 'wait'):
            downvotes.query.filter_by(id=deletedv).delete()
            data['status'] = 'success'
        else:
            return errorHandler.throwError('Only posts that are waiting for a downvote can be removed. Duh!')

    else:
        # get users
        users_schema = usersSchema(many=True)
        users_table = users.query.filter_by().order_by(users.created.desc())
        results = users_schema.dump(users_table)
        usersl = []

        for row in results:
            user = row
            user['delegator'] = 0
            delegations = client.get_vesting_delegations(
                user['account'], 'curangel', 1)
            if len(delegations) > 0 and delegations[0]['delegatee'] == 'curangel':
                user['delegator'] = 1
            usersl.append(user)
        data['users'] = usersl
        print(data['users'])
        # get upvotes
        #upvotes_schema = upvotesSchema(many=True)
        #upvote_table = upvotes.query.filter_by().order_by(upvotes.created.desc())
        #dataJson = upvotes_schema.dump(upvote_table)
        #data['upvotes'] = dataJson

        # check if posts have been voted by us
        #i = 0
        # for dic in data['upvotes']:
        #    for key in data['upvotes'][i]:
        #        if key == 'link':
        #            if(was_voted_post(data['upvotes'][i][key])):
        #                print("This post has been voted")
        #                upvotes_schema = upvotesSchema()
        #                upvotes.query.filter_by(
        #                    id=data['upvotes'][i]['id']).delete()
        #                db.session.commit()
        #            else:
        #                print("This post hasn't been voted")
        #                print(data['upvotes'][i]['id'])
        #    i = i+1

        # get upvotes
        upvote_table = upvotes.query.filter_by().order_by(upvotes.created.desc())
        data['upvotes'] = upvotes_schema.dump(upvote_table)

        # get blacklist
        blacklist_table = blacklist.query.filter_by().order_by(blacklist.created.desc())
        data['blacklist'] = blacklist_schema.dump(blacklist_table)

        # get downvote
        downvote_table = downvotes.query.filter_by().order_by(downvotes.created.desc())
        data['downvotes'] = downvotes_schema.dump(downvote_table)
    return data


def was_voted_post(post_link):
    hived_nodes = [
        'https://api.pharesim.me',
        'https://anyx.io',
        'https://api.hive.blog',
        'https://api.openhive.network',
    ]

    user = "moo-cow"
    key = "5Jkmw272v8mF21RCWG6KveFyKJdXTsCc8w19uYgzLkmAUJB1XhE"
    client = Hive(keys=[key], nodes=hived_nodes)
    link = post_link.split('/')
    post = client.get_content(link[-2][1:], link[-1])

    # check if already voted
    for vote in post['active_votes']:
        if vote['voter'] == 'terminado':
            return True
    return False


@app.route('/downvote', methods=['GET', 'POST'])
@login_required
def downvote():
    hived_nodes = [
        'https://api.pharesim.me',
        'https://anyx.io',
        'https://api.hive.blog',
        'https://api.openhive.network',
    ]
    client = Hive(nodes=hived_nodes)
    chain = Blockchain(client)

    # whitelist
    whitelist = [
        'pharesim', 'azircon', 'nikv', 'tazi', 'galenkp', 'joshmania', 'lemony-cricket'
    ]

    # output variable
    data = {}

    # get and set variables
    username = None
    userhash = None
    postlink = None
    limit = None
    reason = None
    deletedv = None
    if 'username' in request.form:
        username = request.form['username']
    if 'userhash' in request.form:
        userhash = request.form['userhash']
    if 'postlink' in request.form:
        postlink = request.form['postlink']
    if 'limit' in request.form:
        limit = request.form['limit']
    if 'reason' in request.form:
        reason = request.form['reason']
    if 'deletedownvote' in request.form:
        deletedv = request.form['deletedownvote']
    print(username, userhash)
    # check permissions
    users_schema = usersSchema()
    result = users.query.filter_by(account=username, hash=userhash).first()
    result = users_schema.dump(result)
    delegator = 0
    delegations = client.get_vesting_delegations(username, 'curangel', 1)

    if len(delegations) > 0 and delegations[0]['delegatee'] == 'curangel':
        delegator = 1
    print(delegations, delegator)
    if len(result) < 1 or delegator == 0:
        return errorHandler.throwError('No permission')

    if limit:
        limit = int(limit)

    if deletedv:
        # post = db.select('downvotes',['status'],{'account':username,'id':deletedv},'status')
        # if len(results) < 1:
        #     errorHandler.throwError('Downvote not found!')
        # db.delete('downvotes',{'id':deletedv})
        # data['status'] = 'success'
        print("Delete Downvote")
    else:
        # submit new post
        if postlink:
            link = postlink.split('#')
            if len(link) > 1:
                link = link[1].split('/')
            else:
                link = postlink.split('/')
            post = client.get_content(link[-2][1:], link[-1])
            # check if reason was given
            if not reason:
                return errorHandler.throwError(
                    'You need to give a reason for the downvote.')
            # check whitelist
            # if username not in whitelist:
            #    errorHandler.throwError(
            #        'To use this tool, please apply in our Discord!')
            # check if user has more than the limit of posts waiting
            #       result = db.select('downvotes',['id'],{'account':username,'status':'wait'},'id')
            #       if len(result) > 2:
            #           errorHandler.throwError('You already have '+len(result)+' posts waiting to be downvoted. Please wait until those are processed.')

            # check if post is in upvote queue
            upvotes_schema = upvotesSchema()
            result = upvotes.query.filter_by(slug=post['permlink']).first()
            result = upvotes_schema.dump(result)

            if len(result) > 0:
                return errorHandler.throwError(
                    'Post was already curated by '+result[0]['account'])

            # check if already voted
            for vote in post['active_votes']:
                if vote['voter'] == 'curangel':
                    return errorHandler.throwError('We already voted on that post.')

            # check if user added that post already
            downvotes_schema = downvotesSchema()
            result = downvotes.query.filter_by(
                account=username, link=post['url'], status='wait').first()
            result = upvotes_schema.dump(result)
            if len(result) > 0:
                return errorHandler.throwError(
                    'You already added this post. Re-adding it would not change anything. If you want to maximize your power on this post, do not add others in this round.')

            # check cashout time
            # cashoutts = time.mktime(datetime.datetime.strptime(
            #    post['cashout_time'], "%Y-%m-%dT%H:%M:%S").timetuple())
            # chaints = time.mktime(datetime.datetime.strptime(
            #    chain.info()['time'], "%Y-%m-%dT%H:%M:%S").timetuple())
            # if cashoutts - chaints < 60*60*24:
            #    errorHandler.throwError(
            #        'Cashout of post in less than 24 hours. Will not add to queue.')

            # check if limit is valid
            # if limit < 10 or limit > 99:
            #    errorHandler.throwError('Invalid limit for downvote weight.')
            # targetreward = round(
            #    float(post['pending_payout_value'][:-4]) * (100-limit) / 100, 3)
            post_type = 1
            if post['parent_author']:
                post_type = 2

            new_downvote = upvotes(account=username, reason=reason, link=post['url'], user=post['author'],
                                   category=post['category'], slug=post['permlink'], title=post['title'], type=post_type, payout=post['cashout_time'], status='wait', reward=post['pending_payout_value'], maxi=targetreward)
            db.session.add(new_downvote)
            db.session.commit()

        # get downvotes
        downvotes_schema = downvotesSchema(many=True)
        downvote_table = downvotes.query.filter_by(
            account=username).order_by(downvotes.created.desc())
        dataJson = downvotes_schema.dump(downvote_table)

        data['downvote'] = dataJson
        api.output(data)
        return data


@app.route('/upvote', methods=['POST'])
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

        # db.session.query(upvotes).filter(
        #    upvotes.id == deleteuv).update({'status': 'canceled'})
        # db.session.commit()
        upvotes.query.filter_by(id=deleteuv).delete()
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
