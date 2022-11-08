# from access import access
import re
import json
from . import app
import hashlib, hmac
from .database import create_conn
from flask_cors import cross_origin
from flask import request, render_template, make_response, redirect, url_for

@app.route('/auth', methods = ("GET","POST"))
@cross_origin()
def auth():
    if request.cookies:
        id = request.cookies.get('id')
        token = request.cookies.get('token')
        if id and token and id.isdigit() and re.fullmatch(r'[a-z0-9]{64}',token):
            sql, db = create_conn()
            sql.execute(f"SELECT COUNT(*) FROM users WHERE id = {id} AND hash = '{token}'")
            isAuth = sql.fetchone()[0]
            db.close()
            if isAuth:
                return redirect(url_for('index'))


    if request.args and request.args.get('hash'):
        data = {key:value for key, value in request.args.items()}
        cheker = check_response(data)
        print(cheker)
        if not cheker:
            return json.dumps({'message': "Ошибка в данных", 'resultCode': 2}, ensure_ascii=False), 200

        sql, db = create_conn()
        sql.execute(f"SELECT COUNT(*) FROM users WHERE id = {data.get('id')}")
        isReg = sql.fetchone()[0]

        if isReg == 1:
            sql.execute(f"""UPDATE users SET hash = '{data.get("hash")}' WHERE id = {data.get('id')}""")
        else:
            sql.execute(f"""INSERT INTO users (id, username, first_name, last_name, hash, photo_code) 
            VALUES ({data.get("id")}, '{data.get("username")}','{data.get("first_name")}','{data.get("last_name")}',
            '{data.get("hash")}', '{data.get("photo_url")}')""")

        db.commit()
        db.close()

        res = make_response(redirect(url_for('index')))
        res.set_cookie('id', data.get('id'), max_age=365*24*3600)
        res.set_cookie('token', data.get('hash'), max_age=365*24*3600)
        return res


    return render_template('login.html', url=request.base_url)


@app.route('/logout', methods = ("GET","POST"))
@cross_origin()
def logout():
    res = make_response(redirect('auth'))
    res.set_cookie('id', '', expires=0)
    res.set_cookie('token', '', expires=0)
    return res


def check_response(data):
    d = data.copy()
    d_list = []
    print(d.get('hash'))
    if not d.get('id','a').isdigit():
        return False
    elif not re.fullmatch(r'[a-z0-9]{64}',d.get('hash')):
        return False

    del d['hash']
    for key in sorted(d.keys()):
        if d.get(key, None):
            d_list.append(key + '=' + str(d[key]))
            
    data_string = bytes('\n'.join(d_list), 'utf-8')

    secret_key = hashlib.sha256(app.config['TELEGRAM_BOT_TOKEN'].encode('utf-8')).digest()
    hmac_string = hmac.new(secret_key, data_string, hashlib.sha256).hexdigest()

    return hmac_string == data['hash']

