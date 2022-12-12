import random
import re
import datetime
from . import app, socketio
from .access import access
from .database import create_conn
from .config import pages
from flask import request, render_template, url_for, send_file
import xlwt
import os
def get_timestamp(date:datetime.datetime=None) -> int:
    date = date or datetime.datetime.now()
    return int(''.join(str(date.timestamp()).split('.'))[0:13].ljust(13,'0'))

@app.route('/',methods=('GET','POST'),endpoint='index')
@access([1,2,3,4,5])
def index():
    sql, db = create_conn()

    data = request.form
    date = datetime.datetime.now()

    start = data.get('start') or (date - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    stop = data.get('stop') or date.strftime('%Y-%m-%d')
    message = []

    if not re.fullmatch('\d{4}-\d{2}-\d{2}', start) or not re.fullmatch('\d{4}-\d{2}-\d{2}', stop):
        return 'Не не не!', 500

    sql.execute('SELECT * FROM cities')
    cities = sql.fetchall()

    sql.execute('SELECT * FROM directions')
    directions = sql.fetchall()

    cities_id = tuple([i[0] for i in cities])
    directions_id = tuple([i[0] for i in directions])
    statuses = ('new', 'agreed', 'rejected')
    order_by = True
    name = ''

    if request.method == 'POST':
        form = request.form

        form_id = form.get('form_id')
        status = form.get('status')

        if form_id and form_id.isdigit() and status  in ('agreed', 'rejected'):

            sql.execute("UPDATE forms SET status = %s WHERE id=%s AND status='new'",(status,form_id))

            message.append(
                {'title':'Изменение статуса анкеты.','message':'Статус анкеты успешно изменён!', 'type':'success'}
                if sql.rowcount == 1 else
                {'title': 'Изменение статуса анкеты.', 'message': 'Ошибка анкета уже была рассмотрена другим сотрудником!', 'type': 'danger'}
            )
            db.commit()

    if request.args:
        form = request.args
        name = form.get('search')
        cities_id = tuple([int(i) for i in form.getlist('city') if i.isdigit()])
        directions_id = tuple([int(i) for i in form.getlist('direction') if i.isdigit()])
        order_by = form.get('order_by')
        statuses = tuple([i for i in form.getlist('status') if i in ('new','agreed','rejected')])

    sql.execute("SELECT to_char(i, 'DD.MM'), COUNT(date) FROM generate_series( date %s,  %s, '1 day'::interval) i LEFT JOIN bot_uses b ON i = b.date GROUP BY i",(start, stop))
    rows = sql.fetchall()

    bot_uses = [[],[]]

    for i in rows:
        bot_uses[0].append(i[0])
        bot_uses[1].append(i[1])

    statuses = statuses or ('',)
    cities_id = cities_id or (0,)
    directions_id = directions_id or (0,)

    sql.execute(f"""SELECT f.id, surname, f.name, f.father_name, email, birthday_date, CAST(extract(years from age(now(), birthday_date)) as int) as years, university, pc.name, c.name, d.name, cover_letter, resume, f.status FROM forms as f INNER JOIN directions as d ON f.direction_id = d.id INNER JOIN cities c on c.id = f.city_id INNER JOIN educations pc on pc.id = f.profession_id WHERE city_id in %s AND direction_id in %s AND status in %s AND f.surname || ' ' || f.name || ' ' || f.father_name LIKE %s ORDER BY f.id {'DESC' if order_by else 'ASC'}""",(cities_id,directions_id, statuses, f'%{name}%'))
    users = sql.fetchall()

    if request.form.get('act-get-data'):

        wb = xlwt.Workbook()
        ws = wb.add_sheet(f"Анкеты")
        titles = ['ID анкеты','Фамилия','Имя','Отчество','Почта','Дата рождения', 'Полных лет','Университет','Направление образования', 'Город','Направление','Сопроводительное письмо','Ссылка на резюме','Статус']
        for i in range(len(titles)):
            ws.write(0, i, titles[i])

        for index, row in enumerate(users, start=1):
            for j, r in enumerate(row):
                if j == 12:
                    r = f'{request.base_url[:-1]}'+url_for('static', filename=f'img/resume/{r}')
                ws.write(index, j, r)

        name = f'changer_{get_timestamp()}.xls'
        wb.save(os.path.join(app.static_folder,'export', name))

        return send_file(os.path.join(app.static_folder,'export', name), as_attachment=True,
                         download_name=f'Выгрузка анкет ДомРФ.xlsx')
    db.close()
    return render_template('index.html', users=users,cities=cities, directions=directions, pages=pages,request=request,
                           bot_uses=bot_uses, start=start, stop=stop, message=message, cities_id=cities_id,
                           directions_id=directions_id, statuses=statuses, name=name)

