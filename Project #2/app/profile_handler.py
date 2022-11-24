import random
import re
import datetime
from . import app, socketio
from .access import access
from .database import create_conn
from .config import pages
from flask import request, render_template, url_for



@app.route('/',methods=('GET','POST'),endpoint='index')
@access(range(7))
def index():
    sql, db = create_conn()

    data = request.form
    date = datetime.datetime.now()

    start = data.get('start') or (date - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    stop = data.get('stop') or date.strftime('%Y-%m-%d')
    message = []

    if not re.fullmatch('\d{4}-\d{2}-\d{2}', start) or not re.fullmatch('\d{4}-\d{2}-\d{2}', stop):
        return 'Не не не!', 500

    if request.method == 'POST':
        form = request.form
        form_id = form.get('form_id')
        status = form.get('status')
        print(form_id, status, form)
        if form_id and form_id.isdigit() and status  in ('agreed', 'rejected'):

            sql.execute('UPDATE forms SET status = %s WHERE id=%s',(status,form_id))
            db.commit()

            message.append({'title':'Изменение статуса анкеты.','message':'Статус анкеты успешно изменён!', 'type':'success'})

    sql.execute("SELECT to_char(i, 'DD.MM'), COUNT(date) FROM generate_series( date %s,  %s, '1 day'::interval) i LEFT JOIN bot_uses b ON i = b.date GROUP BY i",(start, stop))
    rows = sql.fetchall()

    bot_uses = [[],[]]

    for i in rows:
        bot_uses[0].append(i[0])
        bot_uses[1].append(i[1])

    sql.execute("""SELECT f.id, f.name, surname, CAST(extract(years from age(now(), birthday_date)) as int) as years, d.name, f.status FROM forms as f INNER JOIN directions as d ON f.direction_id = d.id ORDER BY f.id DESC""")
    users = sql.fetchall()
    db.close()

    return render_template('index.html', users=users, pages=pages,request=request, bot_uses=bot_uses, start=start, stop=stop, message=message)

