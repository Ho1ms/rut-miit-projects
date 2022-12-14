import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from .config import pages, TOKEN
from flask import request, url_for, render_template
from flask_socketio import join_room, leave_room
import requests


@socketio.on('join')
def on_join(data):
    id = data.get('id')
    token = data.get('token')

    if not id or not token:
        return

    sql, db = create_conn()

    sql.execute(f"""SELECT id FROM users WHERE id = %s AND hash = %s AND role_id < 6""", (id, token))
    row = sql.fetchone()
    db.close()

    if row:
        room = data.get('room')
        join_room(room)

@socketio.on('leave')
def on_leave(data):
    room = data.get('room')
    leave_room(room)

@app.route('/tickets', endpoint='tickets')
@access([1,2,3,4,5])
def tickets():
    sql, db = create_conn()
    sql.execute("SELECT id, user_name, question, status, coalesce(admin_name, 'Нет'), to_char(create_date, 'HH24:MI:SS DD.MM.YYYY') FROM tickets ORDER BY id DESC")
    tickets = sql.fetchall()
    db.close()
    return render_template('tickets.html', pages=pages, tickets=tickets)

@app.route('/tickets/<int:id>',methods=('GET','POST'), endpoint='ticket_page')
@access([1,2,3,4,5])
def ticket_page(id):
    sql, db = create_conn()
    if request.method == 'POST':
        data = request.json
        sql.execute(f"SELECT user_id FROM tickets WHERE id={id} AND status!='closed'")
        r = sql.fetchone()
        if data.get('action') == 'close-ticket':

            user_id = data.get('user_id')
            user_id = user_id if type(user_id)==int else 0
            sql.execute(f"UPDATE tickets SET status='closed', close_date=CURRENT_TIMESTAMP WHERE id={id} AND (admin_id={request.cookies.get('id')} OR user_id={user_id})")
            db.commit()
            if r:
                requests.post(url=f'https://api.telegram.org/bot{TOKEN}/sendMessage', data={'chat_id': r[0], 'text': 'Сеанс был прекращён.', 'parse_mode': "HTML"})

            socketio.emit('close_ticket',to=f'/tickets/{id}')

            db.close()
            return {'close_ticket':True},200
        else:

            if r:
                sql.execute(f"INSERT INTO ticket_messages (author_id, text, ticket, author_name, author_img) VALUES (%s, %s, {id},%s,%s) ", (data.get('user_id'),data.get('text'), data.get('name'), data.get('img')))
                db.commit()
                if request.cookies.get('is_bot') is None:
                    requests.post(url=f'https://api.telegram.org/bot{TOKEN}/sendMessage', data={'chat_id': r[0], 'text': data.get('text'),'parse_mode':"HTML"})
                socketio.emit('new_message',{'name':data.get('name'), 'text':data.get('text'), 'avatar':data.get('img'), 'is_bot':request.cookies.get('is_bot')}, to=f'/tickets/{id}')
                db.close()
                return {'active':True}, 200
            db.close()
            return {'active': False}, 200

    sql.execute(f"SELECT author_id, author_name, author_img, text, to_char(date, 'HH24:MI:SS DD.MM.YYYY') FROM ticket_messages WHERE ticket={id} ORDER BY id ")
    messages = sql.fetchall()

    sql.execute(f"SELECT user_id, user_name, user_img, question, to_char(create_date, 'HH24:MI:SS DD.MM.YYYY'), status FROM tickets WHERE id={id}")
    row = sql.fetchone()

    sql.execute(f"SELECT first_name || ' ' || last_name, photo_code FROM users WHERE id={request.cookies.get('id')}")
    author = sql.fetchone()

    sql.execute(f"UPDATE tickets SET status = 'active', answer_date=CURRENT_TIMESTAMP, admin_id={request.cookies.get('id')}, admin_name=%s WHERE id={id} AND status='new'", (author[0],))
    db.commit()

    user = {
        'id':row[0],
        'name':row[1],
        'img':row[2],
        'date':row[4],
        'question':row[3],
        'status':row[5]
    }

    db.close()
    return render_template('ticket_chat.html', pages=pages, messages=messages, user=user, author=author)

