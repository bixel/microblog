import os
import re
from jinja2 import evalcontextfilter, Markup, escape
from flask import g, render_template, request, make_response, redirect, url_for, session, abort, jsonify, escape, flash
import flaskext.couchdb as couchdb
import datetime
from urllib.parse import quote
from werkzeug.utils import secure_filename
from app import app

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

manager = couchdb.CouchDBManager()

class User(couchdb.Document):
    doc_type = 'User'

    username = couchdb.TextField()
    displayname = couchdb.TextField()
    password = couchdb.TextField()
    relationship = couchdb.TextField()

    def sha1hash(self, salt, string):
        """ Generate sha1 hash from salt+string
        """
        import hashlib
        return hashlib.sha1(
            '{}{}'.format(salt, string).encode('utf-8')
        ).hexdigest()

    def set_password(self, raw_password):
        """ Encrypt password in django-style and store
            set password to 'algorithm$salt$hash'
        """
        import random
        algo = 'sha1'
        salt = self.sha1hash(str(random.random()), str(random.random()))[:5]
        hsh = self.sha1hash(salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        algo, salt, hsh = self.password.split('$')
        return hsh == self.sha1hash(salt, raw_password)

manager.add_document(User)

class Post(couchdb.Document):
    doc_type = 'Post'

    author_user_id = couchdb.TextField()
    text = couchdb.TextField()
    created = couchdb.DateTimeField(default=datetime.datetime.now)
    filename = couchdb.TextField()
    image = couchdb.TextField()
    deleted = couchdb.BooleanField(default=False)

    def page(self):
        """ Try to clone the paginate format: [["2014-08-22T14:21:00Z", null], "676b4679cdcd56b936a8735022015bbd"]
        """
        from flask import json
        dump = json.dumps([[self.created.isoformat() + "Z", None], self.id])
        return dump

    def get_file(self):
        return 'img/upload/' + self.filename

    all_posts_view = couchdb.ViewField(
        'Post',
        '''\
        function (doc) {
            if (doc.doc_type == 'Post' && !doc.deleted){
                emit([doc.created, doc.id], doc);
            }
        };
        ''',
        descending = True,
    )

manager.add_document(Post)

# Custom jinja filter nl2br
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def validate_user(username, password):
    user = User.load(username)
    if user != None and user.check_password(password):
        return user

    return None


def get_error_message():
    from flask import session
    if 'error_message' in session:
        error_message = session["error_message"]
        session.pop('error_message', None)
        return error_message

    return None


def allowed_file(filename):
    """ Check fileextension
    """
    return ('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS)


@app.route('/', methods=['GET'])
def index():
    page = couchdb.paginate(Post.all_posts_view, 5, start=request.args.get("start"))
    error_message = get_error_message()
    return render_template(
        "index.html",
        title = 'Home',
        page = page,
        error_message = error_message,
    )

@app.route('/json/', methods=['GET'])
def json():
    """ Return a single Post, packed in JSON.
        If no ?post parameter is passed,
    """
    if 'post' in request.args:
        page = couchdb.paginate(Post.all_posts_view, 1, start=request.args.get('post'))
        print(page.prev)
        post = page.items[0]
        return jsonify(
            username=escape(post.author_user_id),
            text=escape(post.text),
            image=post.image,
            next=(quote(page.next) if page.next else ''),
            previous=(quote(page.prev) if page.prev else ''),
            created=post.created,
            id=post.id,
            this=quote(post.page()),
        )

    abort(404)


@app.route('/newpost/', methods=['GET', 'POST'])
def new_post():
    username = (session['username'] if 'username' in session else None)
    if username == None:
        abort(401)

    if request.method == 'POST':
        new_post = Post(author_user_id=username)
        if('text' in request.form):
            new_post.text = request.form['text']
        if('file' in request.form):
            new_post.image = request.form['file']
        new_post.store()
        response = make_response(redirect(url_for('index')))
        return response

    return render_template("new_post.html")


@app.route('/post/', methods=['POST'])
def post():
    if('id' in request.form):
        post = Post.load(request.form['id'])
        if('hide' in request.form and request.form['hide'] == 'True'):
            if(post.author_user_id != session["username"]):
                abort(401)

            post.deleted = True
        post.store()
        flash('Post deleted successfully', 'info')
        return 'post updated'

    flash('Something went wrong...', 'error')
    abort(404)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = validate_user(
            request.form["username"],
            request.form["password"]
        )
        if user != None:
            resp = make_response(redirect(url_for('index')))
            session['username'] = user.username
            return resp
        abort(401)
    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('index')))
    return resp

@app.route('/register/', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        if User.load(request.form['username']) != None:
            return 'Username in use'
        else:
            new_user = User(
                username = request.form['username'],
            )
            new_user.id = request.form['username']
            if(request.form['password'] == request.form['password_check']):
                new_user.set_password(request.form['password'])
                new_user.store()
                return 'User added successfully!'
            else:
                return 'Passwords do not match...'
    else:
        return render_template(
            'new_user.html'
        )

@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if not 'username' in session:
        abort(401)

    username = session['username']
    user = User.load(username)
    if request.method == 'POST':
        user.displayname = request.form["displayname"]
        user.relationship = request.form["relationship"]
        password = request.form["password"]
        password_check = request.form["password-check"]
        if(password != ''):
            if password == password_check:
                user.set_password(password)
                flash('Password updated', 'info')
            else:
                flash('Is this your first password-form-thing? Type them twice, yo!', 'error')
        user.store()
        response = make_response(redirect(url_for('profile')))

    return render_template(
        'profile.html',
        user=user
    )


@app.route('/debug/', methods=['GET'])
def debug():
    if not 'username' in session or session['username'] != 'bixel':
        abort(401)

    page = couchdb.paginate(Post.all_posts_view, 1)
    return render_template(
        'debug.txt',
        page=page
    )

manager.setup(app)
manager.sync(app)

app.secret_key = 'öasödfjnsofna.sdfas9f0zpahlsfß1ßu4hn'
