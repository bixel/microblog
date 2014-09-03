from flask import Flask
import config

UPLOAD_PATH = 'app/static/img/upload/'

app = Flask(__name__)
app.config['COUCHDB_SERVER'] = 'http://%s%s@localhost:21902/' % (config.username, ':' + config.password)
app.config['COUCHDB_DATABASE'] = 'soak'
app.config['UPLOAD_PATH'] = UPLOAD_PATH
from app import views
