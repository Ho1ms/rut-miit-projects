import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from flask import request, url_for


@app.route('/tickets', endpoint='tickets')
@access([1,2])
def tickets():
    return 'piiiing'
