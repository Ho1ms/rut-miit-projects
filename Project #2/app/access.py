import json
import re

from .database import create_conn
from flask_cors import cross_origin
from flask import redirect, url_for, request
def access(access_roles ):

    def func_inner(func):
        @cross_origin()
        def inner(**kwargs):
            id = request.cookies.get('id', '1')
            token = request.cookies.get('token','1'*64)

            if (not id.isdigit()) or (not re.fullmatch(r'[a-z0-9]{64}', token)):
                return redirect(url_for('auth'))

            sql, db = create_conn()


            sql.execute(f"""SELECT role_id FROM users WHERE id = %s AND hash = %s""", (id, token))
            row = sql.fetchone()
            db.close()


            if not row:
                return redirect(url_for('auth'))
            elif row[0] not in access_roles:
                return json.dumps({'message': 'У вас нет доступа к этой странице!', 'resultCode':2},ensure_ascii=False), 200
            elif request.path == url_for('auth') and row[1]:
                return redirect(url_for('index'))

            return func(**kwargs)

        return inner
    return func_inner