#! /usr/bin/env python2
# coding: utf-8
from __future__ import unicode_literals

from flask import (Flask,
                   request,
                   make_response,
                   session,
                   jsonify,
                   redirect,
                   flash,
                   url_for,
                   render_template)
from flask.ext.socketio import SocketIO, send
from peewee import JOIN_LEFT_OUTER
from database import Post, Comment, User, Like
import config
import json

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['DEBUG'] = True
socketio = SocketIO(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            user = User.get(User.username == username)
            if user.check_password(password):
                session['user_id'] = user.id
                return make_response(redirect(url_for('index')))
            else:
                flash('Möp')
        except:
            flash('Möööp')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    session.clear()
    return make_response(redirect(url_for('index')))


@socketio.on('get_posts')
def get_posts(data):
    if 'offset' not in data:
        data['offset'] = 0
    if 'rows' not in data:
        data['rows'] = 10
    query = (Post
             .select(Post, Comment, Like)
             .join(Comment, JOIN_LEFT_OUTER)
             .switch(Post)
             .join(Like, JOIN_LEFT_OUTER)
             .order_by(Post.id.desc())
             .offset(data['offset'])
             .limit(data['rows']))
    postObjects = []
    for p in query:
        comments = [c.to_dict() for c in p.comment_set]
        likes = [l.user.id for l in p.like_set]
        print(likes)
        pObj = p.to_dict()
        pObj.update({
            'comments': comments,
            'likes': likes
        })
        postObjects.append(pObj)
    send(json.dumps({'posts': postObjects}))


@socketio.on('new_post')
def new_post(data):
    print(session)
    if 'user_id' in session:
        user = User.get(id=session['user_id'])
        p = Post.create(author=user, text=data['text'])
        pObj = p.to_dict()
        pObj.update({
            'comments': [],
            'likes': []
        })
        send(json.dumps({'post': pObj}), broadcast=True)


@socketio.on('like')
def like(data):
    state = False
    try:
        Like.create(post=data['post_id'], user=session['user_id'])
        state = True
    except:
        l = Like.get(post=data['post_id'], user=session['user_id'])
        l.delete_instance()
    send(json.dumps({'like': {
        'post_id': data['post_id'],
        'user_id': session['user_id'],
        'state': state
    }}), broadcast=True)


@socketio.on('auth')
def is_authenticated(data):
    if('user_id' in session):
        send(json.dumps({
            'user_id': session['user_id']
        }))


if __name__ == '__main__':
    socketio.run(app, host=config.HOST, port=config.PORT)
