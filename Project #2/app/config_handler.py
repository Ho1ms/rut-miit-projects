import json
import datetime
from .access import access
from . import app, socketio
from .database import create_conn
from .config import pages
from flask import request, url_for, render_template


@app.route('/config', methods=('POST','GET'), endpoint='tech')
@access([1,2,6])
def tech():
    sql, db = create_conn()
    if request.method == 'POST':
        data = request.form

        if data.get('id') is not None and not data.get('id').isdigit():
            db.close()

            return 'Ай, ай, ай, это что за пакость?',500

        if data.get('act-save-start') or data.get('act-save-contact') or data.get('act-save-faq'):
            sql.execute(f"UPDATE buttons SET title=%s, answer=%s WHERE id = %s",(data.get('title'), data.get('answer'), data.get('id')))
        elif data.get('act-del-faq') and int(data.get('id')) > 2:
            sql.execute("DELETE FROM buttons WHERE id=%s AND type='faq'",(data.get('id'),))
        elif data.get('act-add-faq'):
            sql.execute("INSERT INTO buttons (type, title, answer) VALUES ('faq',%s,%s)",(data.get('title'),data.get('answer')))
        else:
            db.close()
            return 'Ой, ой, ой, что-то пошло не так', 500
        db.commit()

    sql.execute(f"SELECT id, type, title, answer FROM buttons ORDER BY id")
    rows = sql.fetchall()
    start_message = rows[0]
    contact_message = rows[1]
    faq_message = rows[2:]
    db.close()
    return render_template('tech.html', pages=pages,request=request, start_message=start_message, contact_message=contact_message,faq_message=faq_message)