import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from .config import pages
from flask import request, url_for, render_template
from os.path import join
from random import choices
def genCode(lenCode:int = 4):
    return ''.join(choices('1234567890qwertyuiopasdfgjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM', k=lenCode))

@app.route('/config', methods=('POST','GET'), endpoint='tech')
@access([1,2,3,4])
def tech():
    sql, db = create_conn()
    if request.method == 'POST':
        data = request.form

        if data.get('id') is not None and not data.get('id').isdigit():
            db.close()

            return 'Ай, ай, ай, это что за пакость?',500

        if data.get('act-save-start') or data.get('act-save-contact') or data.get('act-save-faq'):
            attachment = ''
            file = request.files.get('file')
            if file:
                filename=genCode(8)+'.jpg'
                file.save(join('app','static','message',filename))
                attachment = f", attachment='{filename}'"
            if not file and data.get('img_edit'):
                attachment = ", attachment=''"
            sql.execute(f"UPDATE buttons SET title=%s, answer=%s {attachment} WHERE id = {data.get('id')}",(data.get('title'), data.get('answer')))
        elif data.get('act-del-faq') and int(data.get('id')) > 2:
            sql.execute("DELETE FROM buttons WHERE id=%s AND type='faq'",(data.get('id'),))
        elif data.get('act-add-faq'):
            file = request.files.get('file')
            filename = ''
            if file:
                filename = genCode(8) + '.jpg'
                file.save(join('app', 'static', 'message', filename))

            sql.execute("INSERT INTO buttons (type, title, answer, attachment) VALUES ('faq',%s,%s,%s)",(data.get('title'),data.get('answer'), filename))
        else:
            db.close()
            return 'Ой, ой, ой, что-то пошло не так', 500
        db.commit()

    sql.execute(f"SELECT id, type, title, answer, attachment FROM buttons ORDER BY id")
    rows = sql.fetchall()
    start_message = []
    contact_message = []
    ticket_message = []
    form_message = []
    faq_messages = []
    faq_message = []

    for i, row in enumerate(rows):
        if row[1] == 'start':
            start_message = row
        elif row[1] == 'contacts':
            contact_message = row
        elif row[1] == 'ticket':
            ticket_message = row
        elif row[1] == 'form':
            form_message = row
        elif row[1] == 'faq':
            faq_messages.append(row)
        elif row[1] == 'faq_main':
            faq_message = row
    db.close()
    return render_template('tech.html', pages=pages,
                           request=request, start_message=start_message,
                           contact_message=contact_message,faq_message=faq_message,
                           ticket_message=ticket_message,form_message=form_message,
                           faq_messages=faq_messages
                           )