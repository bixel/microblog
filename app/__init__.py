from flask import Flask

app = Flask(__name__)
app.config['COUCHDB_SERVER'] = 'http://127.0.0.1:5984/'
app.config['COUCHDB_DATABASE'] = 'soak'
from app import views
