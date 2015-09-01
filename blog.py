#! /usr/bin/env python3
from flask import (Flask,
                   jsonify,
                   request,
                   render_template)

from database import User, Post, Relationship, Likes
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
