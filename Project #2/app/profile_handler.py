import random
import re
import datetime
from . import app, socketio
from .access import access
from .database import create_conn
from flask import request, render_template, url_for



@app.route('/',endpoint='index')
@access(range(7))
def index():
    sql, db = create_conn()
    sql.execute("""SELECT f.id, f.name, surname, CAST(extract(years from age(now(), birthday_date)) as int) as years, d.name FROM forms as f INNER JOIN directions as d ON f.direction_id = d.id ORDER BY f.id DESC""")
    users = sql.fetchall()
    db.close()
    pages = [
        {'title':'Главная','path':'index', 'icon':'graph-up'},
        {'title':'Тикеты','path':'tickets', 'icon':'headset'},
        {'title':'Настройки бота','path':'tech', 'icon':'toggles'},
        {'title':'Тех. поддержка','path':'tech', 'icon':'menu-button-wide'}
    ]
    return render_template('index.html', users=users, pages=pages,request=request)

@app.route('/tech', endpoint='tech')
@access(range(7))
def tech():
    users = []
    names = (
    'Андрей', 'Данила', 'Александр', 'Борис', 'Владимир', 'Олег', 'Семён', 'Пётр', 'Алексей', 'Ярослав', 'Кирилл')
    lasts = (
    'Игольников', 'Латышев', 'Иванов', 'Гаганов', 'Покусаев', 'Бирюков', 'Петров', 'Антонов', 'Кудинов', 'Смыгалин',
    'Яшин', 'Юсупов', 'Хромушкин')
    types = ('Новые горизонты', 'Смотрим в будущее', 'Открываем путь', 'Дорогу молодым')
    for i in range(1, 100):
        users.append((
            i,
            random.choice(names),
            random.choice(lasts),
            random.randint(19, 54),
            random.choice(types)

        ))
    pages = [
        {'title': 'Главная', 'path': 'index', 'icon': 'graph-up'},
        {'title': 'Тикеты', 'path': 'tickets', 'icon': 'headset'},
        {'title': 'Настройки бота', 'path': 'tech', 'icon': 'toggles'},
        {'title': 'Тех. поддержка', 'path': 'tech', 'icon': 'menu-button-wide'}
    ]
    return render_template('index.html', users=users, pages=pages, request=request)

@app.route('/tickets', endpoint='tickets')
@access(range(7))
def tech():
    users = []
    names = (
    'Андрей', 'Данила', 'Александр', 'Борис', 'Владимир', 'Олег', 'Семён', 'Пётр', 'Алексей', 'Ярослав', 'Кирилл')
    lasts = (
    'Игольников', 'Латышев', 'Иванов', 'Гаганов', 'Покусаев', 'Бирюков', 'Петров', 'Антонов', 'Кудинов', 'Смыгалин',
    'Яшин', 'Юсупов', 'Хромушкин')
    types = ('Новые горизонты', 'Смотрим в будущее', 'Открываем путь', 'Дорогу молодым')
    for i in range(1, 100):
        users.append((
            i,
            random.choice(names),
            random.choice(lasts),
            random.randint(19, 54),
            random.choice(types)

        ))
    pages = [
        {'title': 'Главная', 'path': 'index', 'icon': 'graph-up'},
        {'title': 'Тикеты', 'path': 'tickets', 'icon': 'headset'},
        {'title': 'Настройки бота', 'path': 'tech', 'icon': 'toggles'},
        {'title': 'Тех. поддержка', 'path': 'tech', 'icon': 'menu-button-wide'}
    ]
    return render_template('index.html', users=users, pages=pages, request=request)
