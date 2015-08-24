from flask import Flask
import config

UPLOAD_PATH = 'app/static/img/upload/'

app = Flask(__name__)
app.config['COUCHDB_SERVER'] = ('http://{}:{}@localhost:{}/'
                                .format(config.username,
                                        config.password,
                                        config.port))
app.config['COUCHDB_DATABASE'] = 'soak'
app.config['UPLOAD_PATH'] = UPLOAD_PATH
