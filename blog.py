#! /usr/bin/env python3
from flask import (Flask,
                   jsonify,
                   make_response,
                   render_template)
from peewee import JOIN_LEFT_OUTER
from database import Post, Comment
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/posts/')
@app.route('/api/posts/<int:page>/')
def posts(page=None):
    query = (Post
             .select(Post, Comment)
             .join(Comment, JOIN_LEFT_OUTER)
             .aggregate_rows())
    if not page:
        page = 1
    query.order_by(Post.id).paginate(page, 10)
    postObjects = []
    for p in query:
        comments = [c.to_dict() for c in p.comment_set]
        pObj = p.to_dict()
        pObj.update({
            'comments': comments
        })
        postObjects.append(pObj)
    return make_response(
        jsonify(posts=postObjects),
        200
    )


if __name__ == '__main__':
    app.run(debug=True)
