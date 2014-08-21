from flask import Flask

UPLOAD_PATH = 'app/static/img/upload/'

app = Flask(__name__)
app.config['COUCHDB_SERVER'] = 'http://127.0.0.1:5984/'
app.config['COUCHDB_DATABASE'] = 'soak'
app.config['UPLOAD_PATH'] = UPLOAD_PATH
from app import views
