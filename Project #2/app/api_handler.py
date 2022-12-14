import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from flask import request, url_for


@app.route('/api/add-use-<int:user_id>', endpoint='add_form')
@access([1,2])
def add_form(user_id):
    sql, db = create_conn()
    sql.execute(f'INSERT INTO bot_uses (user_id) VALUES ({user_id}) ON CONFLICT DO NOTHING')
    db.commit()
    db.close()
    return {'message':'success'},200


@app.route('/api/get-form', endpoint='get_form')
@access([1,2])
def get_form():
    id = request.args.get('id')

    if not id or not id.isdigit():
        return 'Not valid',400

    sql, db = create_conn()
    names = ['id','user_id','name', 'surname', 'father_name',
             'city','years','date','direction','email','cover_letter', 'resume', 'university','education', 'username']

    sql.execute(f"""SELECT f.id, user_id, f.name, surname, 
    father_name, c.name, CAST(extract(years from age(now(), birthday_date)) as int) as years,
     to_char(birthday_date, 'dd.mm.YYYY') as date, d.name, email, cover_letter, resume, university,  b.name, username
    FROM forms as f 
    INNER JOIN directions as d ON f.direction_id = d.id 
    INNER JOIN cities as c ON c.id = f.city_id 
    INNER JOIN educations as b ON b.id = f.profession_id 
    WHERE f.id = {id}""")
    row = sql.fetchone() or []
    data = {key:row[i] if i < len(row) else None for i, key in enumerate(names)}
    db.close()
    return json.dumps(data, ensure_ascii=False),200

get_tables = {
    'directions':['id','name'],
    'cities':['id','name'],
    'profession_codes':['id','code','title'],
    'educations':['id','name']
}

@app.route('/api/get-<table>', endpoint='get_directions')
@access([1,2])
def get_table(table):
    if table not in get_tables:
        return {'message':'Unknown table','resultCode':2},200

    sql, db = create_conn()
    sql.execute(f"""SELECT {', '.join(get_tables[table])} FROM {table}""")
    rows = sql.fetchall()
    db.close()
    return json.dumps({'data': rows}, ensure_ascii=False),200



@app.route('/api/form-handler', methods=('POST',), endpoint='form_handler')
@access([1,2])
def form_handler():
    data = request.json
    sql, db = create_conn()

    data['birthday_date'] = datetime.datetime.strptime(data['birthday_date'], '%d.%m.%Y').strftime('%Y-%m-%d')
    names = ['user_id','name', 'surname', 'father_name', 'city_id','birthday_date',
             'direction_id','email','cover_letter', 'resume', 'university','profession_id', 'username']
    sql.execute(f"""INSERT INTO forms ({", ".join(names)}) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",(*[data.get(i) for i in names],))

    return_id = sql.fetchone()[0]
    db.commit()

    sql.execute(
        f"""SELECT f.id, f.name, f.surname, f.father_name, d.name, c.name, CAST(extract(years from age(now(), birthday_date)) as int) as years, status
        FROM forms as f INNER JOIN directions as d ON f.direction_id = d.id INNER JOIN cities c on c.id = f.city_id WHERE f.id = {return_id}""")
    row = sql.fetchone()
    db.close()

    body = {
        'id': row[0],
        'name':row[1],
        'surname':row[2],
        'father': row[3],
        'direction': row[4],
        'city': row[5],
        'years': row[6],
        'type': row[7]
    }
    socketio.emit('add-form',body)

    notify_body = {
        'title':'?????????? ????????????!',
        'description':f'???????????? ???? {data["name"]} {data["surname"]}',
        'icon': url_for('static',filename="Logo.jpg")
    }
    socketio.emit('notify',notify_body)

    return {'data': body},200

@app.route('/api/get-<type>-<type_2>', endpoint='get_start_message')
@access([1,2])
def get_start_message(type, type_2):
    if type not in ('faq','start','contacts', 'form','ticket','faq_main') or type_2 not in ('messages','message'):
        return 'Unknown type',404
    sql, db = create_conn()
    sql.execute('SELECT title, answer, attachment, id FROM buttons WHERE type = %s',(type,))


    if type_2 == 'message':
        row = sql.fetchone()
        data = {
            'id':row[3],
            'title': row[0] ,
            'text': row[1] ,
            'attachment': row[2] or ''
        }
    elif type_2 == 'messages':
        rows = sql.fetchall()
        data = []
        for row in rows:
            data.append(
                {
                    'id':row[3],
                    'title': row[0] ,
                    'text': row[1],
                    'attachment': row[2] or ''
                }
            )

    db.close()

    return json.dumps(data, ensure_ascii=False), 200

@app.route('/create-ticket',methods=('POST',), endpoint='create_ticket')
@access([1,2])
def create_ticket():
    data = request.json
    user = data.get('user')

    sql, db = create_conn()

    sql.execute(f"INSERT INTO tickets (user_id, user_name, user_img, question) VALUES (%s,%s,%s,%s) RETURNING id",(user.get('id'),user.get('name'),user.get('img'),data.get('message')))
    row = sql.fetchone()[0]

    db.commit()
    db.close()
    notify_body = {
        'title':'?????????? ??????????!',
        'description':f'???????????????????????? {user.get("name")} ???????????? ??????????!',
        'icon': url_for('static',filename="Logo.jpg")
    }
    socketio.emit('notify',notify_body)

    socketio.emit('new_ticket',{'id':row,'message':data.get('message'),'username':user.get('name')})
    return {'id':row}, 200