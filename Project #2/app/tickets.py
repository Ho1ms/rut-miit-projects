import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from .config import pages
from flask import request, url_for, render_template


@app.route('/tickets', endpoint='tickets')
@access([1,2,3,4,5])
def tickets():
    sql, db = create_conn()
    sql.execute("SELECT id, user_name, question, status, admin_name, to_char(create_date, 'HH24:MI:SS DD.MM.YYYY') FROM tickets ORDER BY id DESC")
    tickets = sql.fetchall()
    db.close()
    return render_template('tickets.html', pages=pages, tickets=tickets)

@app.route('/tickets/<int:id>',methods=('GET','POST'), endpoint='ticket_page')
@access([1,2,3,4])
def ticket_page(id):
    sql, db = create_conn()
    if request.method == 'POST':
        data = request.json
        sql.execute(f"INSERT INTO ticket_messages (author_id, text, ticket, author_name, author_img) VALUES ({request.cookies.get('id')}, %s, {id},%s,%s) ", (data.get('text'), data.get('name'), data.get('img')))
        db.commit()
        socketio.emit('new_message',{'name':data.get('name'), 'text':data.get('text'), 'avatar':data.get('img')}, namespace=f'/tickets/{id}')
        return {}, 200
    sql.execute(f"SELECT author_id, author_name, author_img, text, to_char(date, 'HH24:MI:SS DD.MM.YYYY') FROM ticket_messages WHERE ticket={id} ORDER BY id ")
    messages = sql.fetchall()

    sql.execute(f"SELECT user_id, user_name, user_img, question, to_char(create_date, 'HH24:MI:SS DD.MM.YYYY') FROM tickets WHERE id={id}")
    row = sql.fetchone()

    sql.execute(f"SELECT first_name || ' ' || last_name, photo_code FROM users WHERE id={request.cookies.get('id')}")
    author = sql.fetchone()
    user = {
        'id':row[0],
        'name':row[1],
        'img':row[2],
        'date':row[4],
        'question':row[3],
    }

    db.close()
    return render_template('ticket_chat.html', pages=pages, messages=messages, user=user, author=author)
