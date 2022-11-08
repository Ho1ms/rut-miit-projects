import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from flask import request, url_for



@app.route('/api/get-form', endpoint='get_form')
@access([1,2,6])
def get_form():
    id = request.args.get('id')
    print(id)
    if not id or not id.isdigit():
        return 'Not valid',400
    print('1234')
    sql, db = create_conn()
    names = ['id','user_id','name', 'surname', 'father_name',
             'city','years','date','direction','email','cover_letter', 'resume']

    sql.execute(f"""SELECT f.id, user_id, f.name, surname, 
    father_name, c.name, CAST(extract(years from age(now(), birthday_date)) as int) as years, to_char(birthday_date, 'dd.mm.YYYY') as date, d.name, email, cover_letter, resume
    FROM forms as f 
    INNER JOIN directions as d ON f.direction_id = d.id 
    INNER JOIN cities as c ON c.id = f.city_id 
    WHERE f.id = {id}""")
    row = sql.fetchone()
    data = {key:row[i] for i, key in enumerate(names)}
    db.close()
    return json.dumps(data, ensure_ascii=False),200


@app.route('/api/get-directions', endpoint='get_directions')
@access([1,2])
def get_directions():
    sql, db = create_conn()
    sql.execute(f"""SELECT id, name FROM directions""")
    rows = sql.fetchall()
    db.close()
    return json.dumps({'data': rows}, ensure_ascii=False),200


@app.route('/api/get-cities', endpoint='get_cities')
@access([1,2])
def get_cities():
    sql, db = create_conn()
    sql.execute(f"""SELECT id, name FROM cities""")
    rows = sql.fetchall()
    db.close()
    return json.dumps({'data': rows}, ensure_ascii=False),200


@app.route('/api/form-handler', methods=('POST',), endpoint='form_handler')
@access([1,2])
def form_handler():
    data = request.json
    sql, db = create_conn()
    data['birthday_date'] = datetime.datetime.strptime(data['birthday_date'], '%d.%m.%Y').strftime('%Y-%m-%d')
    names = ['user_id','name', 'surname', 'father_name', 'city_id','birthday_date','direction_id','email','cover_letter', 'resume']
    sql.execute(f"""INSERT INTO forms ({", ".join(names)}) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",(*[data.get(i) for i in names],))

    return_id = sql.fetchone()[0]
    db.commit()

    sql.execute(
        f"""SELECT f.id, f.name, f.surname, CAST(extract(years from age(now(), birthday_date)) as int) as years, d.name 
        FROM forms as f INNER JOIN directions as d ON f.direction_id = d.id WHERE f.id = {return_id}""")
    row = sql.fetchone()
    db.close()

    body = {
        'id': row[0],
        'name':row[1],
        'surname':row[2],
        'years': row[3],
        'type': row[4]
    }
    socketio.emit('add-form',body)
    notify_body = {
        'title':'Новая анкета!',
        'description':f'Анкета от {data["name"]} {data["surname"]}',
        'icon': url_for('static',filename="Logo.jpg")
    }
    socketio.emit('notify',notify_body)

    return {'message':'success'},200

@app.route('/api/get-start-message', endpoint='get_start_message')
@access([1,2])
def get_start_message():
    sql, db = create_conn()
    sql.execute('SELECT description, attachment FROM messages LIMIT 1')
    row = sql.fetchone()
    db.close()
    data = {
        'text':row[0],
        'attachment': url_for('static',filename=f'message/{row[1]}') if row[1] else ''
    }

    return json.dumps(data, ensure_ascii=False), 200

