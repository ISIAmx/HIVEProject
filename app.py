from flask import Flask
import flask
import time
import datetime
import random
import string
from flask import render_template, redirect, url_for, request
from flask import json, jsonify
from secrets import randbelow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_marshmallow import Marshmallow
from marshmallow import Schema
from hive.hive import Hive
from hive.blockchain import Blockchain
from hive.account import Account
from sqlalchemy import func
from lib import db_sqlite
from lib import api
from lib import errorHandler

from lib.errors import CurangelError
from lib.account_util import Account

from lib.rate_limit import Enforcer, RateLimitError
from lib.db_util import QueueDBHelper

app = Flask(__name__)
app.config.from_object('config.DevConfig')  # Configuracion Desarrollador
db = SQLAlchemy(app)
ma = Marshmallow(app)


class users(db.Model):
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


class upvotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    payout = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    vote_time = db.Column(db.DateTime, nullable=True)
    reward_sbd = db.Column(db.String(30), nullable=False)
    reward_sp = db.Column(db.String(30), nullable=False)


class downvotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    payout = db.Column(db.DateTime, nullable=False)
    reward = db.Column(db.String(30), nullable=False)
    maxi = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False)

class upvote_notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, server_default=func.now(), nullable=False)

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

class upvote_notifications:
    class Meta:
        fields = ('id', 'user', 'reason', 'created')


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
    deletedv = None
    blackl = None
    reason = None
    deletebl = None

    # Schemas
    users_schema = usersSchema()
    upvotes_schema = upvotesSchema()
    blacklist_schema = blacklistSchema()
    downvotes_schema = downvotesSchema()
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
        upvotes_schema = upvotesSchema(many=True)
        upvote_table = upvotes.query.filter_by().order_by(upvotes.created.desc())
        data['upvotes'] = upvotes_schema.dump(upvote_table)

        # get blacklist
        blacklist_schema = blacklistSchema(many=True)
        blacklist_table = blacklist.query.filter_by().order_by(blacklist.created.desc())
        data['blacklist'] = blacklist_schema.dump(blacklist_table)

        # get downvote
        downvotes_schema = downvotesSchema(many=True)
        downvote_table = downvotes.query.filter_by().order_by(downvotes.created.desc())
        data['downvotes'] = downvotes_schema.dump(downvote_table)
    return data


@app.route('/downvote', methods=['GET', 'POST'])
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

    # schemas
    downvotes_schema = downvotesSchema()
    users_schema = usersSchema()
    upvotes_schema = upvotesSchema()
    # schemas

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

    # check permissions
    result = users.query.filter_by(account=username, hash=userhash).first()
    result = users_schema.dump(result)
    delegator = 0
    delegations = client.get_vesting_delegations(username, 'curangel', 1)

    if len(delegations) > 0 and delegations[0]['delegatee'] == 'curangel':
        delegator = 1

    if len(result) < 1 or delegator == 0:
        return errorHandler.throwError('No permission')

    if limit:
        limit = int(limit)

    if deletedv:
        result = downvotes.query.filter_by(
            account=username, id=deletedv).first()
        result = upvotes_schema.dump(result)

        if len(result) < 1:
            return errorHandler.throwError('Downvote not found!')
        downvotes.query.filter_by(id=deletedv).delete()
        db.session.commit()
        data['status'] = 'success'

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
            if username not in whitelist:
                return errorHandler.throwError('To use this tool, please apply in our Discord!')
            # check if user has more than the limit of posts waiting
            #       result = db.select('downvotes',['id'],{'account':username,'status':'wait'},'id')
            #       if len(result) > 2:
            #           errorHandler.throwError('You already have '+len(result)+' posts waiting to be downvoted. Please wait until those are processed.')

            # check if post is in upvote queue
            result = upvotes.query.filter_by(slug=post['permlink']).first()
            result = upvotes_schema.dump(result)

            if len(result) > 0:
                return errorHandler.throwError(
                    'Post was already curated by '+result['account'])

            # check if already voted
            for vote in post['active_votes']:
                if vote['voter'] == 'curangel':
                    return errorHandler.throwError('We already voted on that post.')

            # check if user added that post already
            result = downvotes.query.filter_by(
                account=username, link=post['url'], status='wait').first()
            result = upvotes_schema.dump(result)
            if len(result) > 0:
                return errorHandler.throwError(
                    'You already added this post. Re-adding it would not change anything. If you want to maximize your power on this post, do not add others in this round.')

            # check cashout time
            cashoutts = time.mktime(datetime.datetime.strptime(
                post['cashout_time'], "%Y-%m-%dT%H:%M:%S").timetuple())
            chaints = time.mktime(datetime.datetime.strptime(
                chain.info()['time'], "%Y-%m-%dT%H:%M:%S").timetuple())
            if cashoutts - chaints < 60*60*24:
                return errorHandler.throwError('Cashout of post in less than 24 hours. Will not add to queue.')

            # check if limit is valid
            if limit < 10 or limit > 99:
                return errorHandler.throwError('Invalid limit for downvote weight.')
            targetreward = round(
                float(post['pending_payout_value'][:-4]) * (100-limit) / 100, 3)
            post_type = 1
            if post['parent_author']:
                post_type = 2
            new_downvote = downvotes(account=username, reason=reason, link=post['url'], user=post['author'],
                                     category=post['category'], slug=post['permlink'], title=post['title'], type=post_type, payout=post['cashout_time'], status='wait', reward=post['pending_payout_value'], maxi=targetreward)
            db.session.add(new_downvote)
            db.session.commit()

        # get downvotes
        downvotes_schema = downvotesSchema(many=True)
        downvote_table = downvotes.query.filter_by(
            account=username).order_by(downvotes.created.desc())

        data['downvotes'] = downvotes_schema.dump(downvote_table)
    return data


@app.route('/upvote', methods=['POST'])
def upvote():
    hived_nodes = [
        'https://api.pharesim.me',
        'https://anyx.io',
        'https://api.hive.blog',
        'https://api.openhive.network',
    ]

    user = "moo-cow"
    key = "5Jkmw272v8mF21RCWG6KveFyKJdXTsCc8w19uYgzLkmAUJB1XhE"
    client = Hive(keys=[key], nodes=hived_nodes)
    chain = Blockchain(client)

    # schemas
    users_schema = usersSchema()
    upvotes_schema = upvotesSchema()
    blacklist_schema = blacklistSchema()
    downvotes_schema = downvotesSchema()
    # schemas

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
    result = users.query.filter_by(account=username).first()
    result = users_schema.dump(result)

    if result['curator'] != True:
        return errorHandler.throwError('No permission')

    # delete post
    if deleteuv:
        posts = upvotes.query.filter_by(account=username, id=deleteuv).first()
        result = upvotes_schema.dump(posts)

        if len(result) < 1:
            return errorHandler.throwError('Upvote not found!')

        # db.session.query(upvotes).filter(
        #    upvotes.id == deleteuv).update({'status': 'canceled'})
        # db.session.commit()
        upvotes.query.filter_by(id=deleteuv).delete()
        db.session.commit()
        data['status'] = 'success'
    else:
        # submit new post
        if postlink:
            link = postlink.split('#')
            if len(link) > 1:
                link = link[1].split('/')
            else:
                link = postlink.split('/')
            post = client.get_content(link[-2][1:], link[-1])
            chaininfo = chain.info()
            print(post['permlink'])
            # check if curator is author himself
            if post['author'] == username:
                return errorHandler.throwError('Curating your own post? Are you serious?')

            # check if curator is author himself
            if post['author'] == 'curangel':
                return errorHandler.throwError('We do not vote for ourselves :D')

            # check if cross post
            metadata = post['json_metadata']
            if metadata != '':
                metadata = json.loads(metadata)
                if 'tags' in metadata:
                    if 'cross-post' in metadata['tags']:
                        return errorHandler.throwError('This is a cross-post. We do not vote on those.')

            # check if author used liquifier
            print(post['permlink'])
            liquifiers = ['likiwid', 'reward.app']
            beneficiaries = post['beneficiaries']
            notification = ''
            for b in beneficiaries:
                if b['account'] in liquifiers:
                    notified = upvote_notifications.query.filter_by(user= post['author'], reason='liquifier')

                    if len(notified) < 1:
                        new_notification = upvote_notifications(
                            user=post['author'], reason='liquifier')
                        db.session.add(new_notification)
                        db.session.commit()
                        notification = 'User has received a comment.'
                        permlink = ''.join(random.sample(
                            string.ascii_lowercase, k=10))
                        body = "Great work! Your post was selected for curation by one of @votame's dedicated curators for its contribution to quality!\n<br />"
                        body += "...unfortunately, it had to be excluded from curation because of the use of a service ("+b[
                            'account']+") to liquify rewards."
                        body += "Our upvotes are reserved for content which is created with a commitment to long term growth and decentralization of Hive Power.\n<br />"
                        body += "This exclusion only applies to this and eventually other future liquified posts and not all your publications in general. \n<br />"
                        body += "Take care and hive five!"
                        #client.commit.post('Re: '+post['title'], body, 'curangel', permlink=permlink,
                        #                reply_identifier='@'+post['author']+'/'+post['permlink'])
                    return errorHandler.throwError('Post is using a liquifier ('+b['account']+') for rewards. Will not add to queue.'+notification)
            # check if already voted
            for vote in post['active_votes']:
                if vote['voter'] == 'curangel':
                    return errorHandler.throwError('We already voted on that post.')

            # check if post has a lot of rewards already

            # check if exists in upvote queue
            result = upvotes.query.filter_by(
                user=post['author'], slug=post['permlink']).first()
            result = upvotes_schema.dump(result)

            if len(result) > 0:
                return errorHandler.throwError(
                    'This post has been submitted before. Will not add to queue again.')

            # check if exists in downvote queue
            result = downvotes.query.filter_by(
                slug=post['permlink'], status='wait').first()
            result = downvotes_schema.dump(result)

            if len(result) > 0:
                return errorHandler.throwError(
                    'Post was already marked for downvote by '+result['account'])

            # check cashout time
            cashoutts = time.mktime(datetime.datetime.strptime(
                post['cashout_time'], "%Y-%m-%dT%H:%M:%S").timetuple())
            chaints = time.mktime(datetime.datetime.strptime(
                chaininfo['time'], "%Y-%m-%dT%H:%M:%S").timetuple())
            if cashoutts - chaints < 60*60*36:
                return errorHandler.throwError('Cashout of post in less than 36 hours. Will not add to queue.')

            # check blacklist
            result = blacklist.query.filter_by(user=post['author']).first()
            result = blacklist_schema.dump(result)

            if len(result) > 0:
                return errorHandler.throwError(
                    'Author blacklistet. Reason: '+result['reason']+'. Will not add to queue.')

            # check previous votes for author
            results = upvotes.query.filter(upvotes.user == post['author'], upvotes.account == username,
                                           upvotes.status != 'canceled', upvotes.created > datetime('now', '-7 days')).all()
            results = upvotes_schema.dump(results)
            if len(results) > 0:
                return errorHandler.throwError('You already submitted a post of this author in the last week. Will not add to queue.')
            results = upvotes.query.filter(
                upvotes.user == post['author'], upvotes.status != 'canceled', upvotes.created > datetime('now', '-1 day')).all()

            if len(results) > 0:
                return errorHandler.throwError('Someone else already submitted a post of this author today. Will not add to queue.')

            # get queue length
            db_path = db_sqlite.config.db.file
            print(db_path)
            # check mana
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

        data['upvotes'] = upvotes_schema.dump(upvote_table)
    return data


if __name__ == '__main__':
    app.run(debug=True)
