import random
import re
import datetime
from . import app, socketio
from .access import access
from .database import create_conn
from .config import pages
from flask import request, render_template, url_for



@app.route('/',endpoint='index')
@access(range(7))
def index():
    sql, db = create_conn()
    sql.execute("""SELECT f.id, f.name, surname, CAST(extract(years from age(now(), birthday_date)) as int) as years, d.name FROM forms as f INNER JOIN directions as d ON f.direction_id = d.id ORDER BY f.id DESC""")
    users = sql.fetchall()
    db.close()

    return render_template('index.html', users=users, pages=pages,request=request)

