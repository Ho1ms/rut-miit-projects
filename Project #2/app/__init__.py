import logging
from flask import Flask
from os import path, getcwd
from .config import *
from flask_socketio import SocketIO
from flask_cors import CORS
from .database import create_conn
log = logging.getLogger('werkzeug')
# log.disabled = True

def dir(folder:str)->str:
    return path.join(getcwd(), 'app', folder)

app = Flask('AIRPORT', static_folder=dir('static'), template_folder=dir('template'))

app.logger.disabled = True
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['TELEGRAM_BOT_TOKEN'] = config.TOKEN

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


socketio = SocketIO(app,engineio_logger=True,logger=True)
socketio.init_app(app, cors_allowed_origins="*")

from . import auth_manager, profile_handler, api_handler, tickets, staff, config_handler, manual


