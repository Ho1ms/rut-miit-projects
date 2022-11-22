import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from .config import pages
from flask import request, url_for, render_template


@app.route('/staff', methods=('GET','POST'),endpoint='staff')
@access([1,2])
def staff():
    sql, db = create_conn()

    sql.execute("SELECT id, title FROM roles ORDER BY id DESC")
    roles_rows = sql.fetchall()
    roles = {role[0]: role[1] for role in roles_rows}

    if request.method == 'POST':
        data = request.form

        id = data.get('id')
        role_id = data.get('role')

        if not id or (id and not id.isdigit()) or (not role_id.isdigit() or int(role_id) not in roles):
            db.close()
            return 'Ай, ай, ай! Это что? Попытка взлома?',500
        else:
            sql.execute("UPDATE users SET first_name = %s, last_name = %s, role_id = %s WHERE id = %s",(data.get('first_name'), data.get('last_name'),role_id, id))
            db.commit()

    search = request.args.get('search')
    if search:

        search = search.replace("'",'').replace(' ','')

        sql.execute(f"SELECT id, username, first_name, last_name, photo_code, role_id FROM users WHERE username LIKE  '%{search}%' OR first_name LIKE  '%{search}%' OR last_name LIKE  '%{search}%' ORDER BY role_id")
    else:
        sql.execute("SELECT id, username, first_name, last_name, photo_code, role_id FROM users ORDER BY role_id")
    users = sql.fetchall()


    db.close()
    return render_template('staff.html',pages=pages, users=users, roles=roles)
