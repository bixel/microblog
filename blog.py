#! /usr/bin/env python2
from __future__ import unicode_literals

from flask import (Flask,
                   render_template)
from flask.ext.socketio import SocketIO, send
from peewee import JOIN_LEFT_OUTER
from database import Post, Comment, User, Like
import config
import json

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('get_page')
def get_page(data):
    if 'page' not in data:
        data['page'] = 1
    if 'rows' not in data:
        data['rows'] = 10
    query = (Post
             .select(Post, Comment, Like)
             .join(Comment, JOIN_LEFT_OUTER)
             .switch(Post)
             .join(Like, JOIN_LEFT_OUTER)
             .aggregate_rows()
             .order_by(Post.id.desc())
             .paginate(data['page'], data['rows']))
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
    user = User.get(id=data['user_id'])
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
        Like.create(post=data['post_id'], user=data['user_id'])
        state = True
    except:
        l = Like.get(post=data['post_id'], user=data['user_id'])
        l.delete_instance()
    send(json.dumps({'like': {
        'post_id': data['post_id'],
        'user_id': data['user_id'],
        'state': state
    }}), broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
