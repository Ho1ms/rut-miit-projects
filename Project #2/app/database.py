import psycopg2
from .config import DB
from os.path import isfile

def create_conn():
    db = psycopg2.connect(**DB)
    sql = db.cursor()
    return sql, db

is_db_init = isfile('db_init')
if not is_db_init:
    db_init = open('start.sql','r',encoding='utf-8')
    print(db_init.read())
    sql, db = create_conn()

    sql.execute(db_init.read())
    db.commit()

    db.close()
    db_init.close()
    open('db_init','w+').read()

