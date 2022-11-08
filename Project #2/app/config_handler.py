import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from flask import request, url_for


# @app.route('/config', endpoint='get_config')
# @access([1,2,6])
# def get_config():
#     sql, db = create_conn()
#     sql.execute(f'')
#     db.close()