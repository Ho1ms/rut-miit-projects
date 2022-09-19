import re
import json
import datetime
import requests
from psycopg2 import connect


connect_data = {'dbname':'','user':'','host':'','password':''}

def create_connect(data:dict):
    db = connect(**data)
    return db, db.cursor()

def getFaculty(year:int,level:int=1,training:int=1):
    """

    year - Год приёма

    level - Тип образования:
    1 - СПО
    2 - СПО на базе 9 классов
    3 - СПО на базе 11 классов
    4 - Бакалавриат и специалитет
    5 - Бакалавриат
    6 - Специалитет
    7 - Магистратура
    8 - Аспирантура

    training Форма обучения:
    20773 - Очная
    20775 - Заочная
    20775 - Очно-заочная

    """
    db, sql = create_connect(connect_data)

    faculties = requests.get(f'https://www.miit.ru/data-service/data/reception-plan?city=1&level={level}&training={training}&year={year}&context_path=&id_lang=1').json()
    results = faculties.get('result')

    if results is None or len(results) == 0:
        return json.dumps({'message':'Данные не найдены!','resultCode':2},ensure_ascii=False)

    array_faculties = []
    array_profiles = []
    for result in results[0].get('concourseGroups'):
        array_faculties.append(f"({result.get('idPlanReception')},'{result.get('specQualifier')}', {level}, {year},'{result.get('specName')}', {training})")

        for profile in result.get('profiles'):
            division = profile.get('division')
            institute_id = re.search('\w+$', division.get('instituteUrl'))
            array_profiles.append(f"('{profile.get('specNote')}', '{institute_id[0] if institute_id is not None else '0'}', '{division.get('instituteAbbreviation')}', '{division.get('instituteName')}', '{profile.get('groupAbbreviation')}')")

    sql.execute( f'INSERT INTO faculties (id, code, level, year, title, trainings) VALUES {", ".join(array_faculties)} ON CONFLICT DO NOTHING')
    if len(array_profiles) > 0:
        sql.execute( f'INSERT INTO institutes (profile_name, institute_id, title, institute_name, group_name) VALUES {", ".join(array_profiles)} ON CONFLICT DO NOTHING')
    db.commit()
    db.close()

def updateFaculties():
    for year in range(2021,datetime.datetime.now().year+1):
        for level in range(1,9):
            for training in (20773,20774,20775):
                getFaculty(year=year,level=level,training=training)

def getStudents(faculty_id:int, year:int):
    """

    :param faculty_id: - ID специальности
    competitions:int - Тип приёма
    0 - Общий конкрус
    1 - Места по договорам
    2 - Целевая квота
    3 - Особая квота
    4 - Специальная квота

    concourseEntrantGroups:int - Тип заявки
    0 - Зачислены
    1 - Участвуют
    2 - Нет баллов
    3 - Баллы ниже минимума
    4 - Забравшие документы
    """

    students = requests.get(f'https://www.miit.ru/data-service/data/entrant-rating?id={faculty_id}&status=all&context_path=&id_lang=1').json()

    if students.get('competitions') is None:
        return json.dumps({'message':'Ошибка получения данных','resultCode':2},ensure_ascii=False)
    arr = []
    for i in range(5):
        if len(students.get('competitions'))-1 < i:
            continue
        if students.get('competitions')[i].get('concourseEntrantGroups',[{'code':0}])[0].get('code') == 0:
            continue

        for student in students.get('competitions')[i].get('concourseEntrantGroups',[{'entrants':[]}])[0].get('entrants'):
            if not student.get('displayName').isdigit() and len(student.get('displayName'))<=5:
                continue
            s = student.get('pointListDisplay') or f'Аттестат: {student.get("points")}'
            isEGE = 'ЕГЭ' in s
            exams = {}
            s = s.replace('ЕГЭ','').replace("ВИ",'')
            for obj in s.split(';'):
                try:
                    disciplin, points = obj.split(':')
                except ValueError:
                    continue

                if student.get('withoutExams'):
                    exams[disciplin] = -1
                    student['points'] = -1
                elif student.get('points', 1) == None:
                    continue
                else:
                    exams[disciplin] = float(points.strip())
            if student.get('points', 1) == None:
                continue
            arr.append(f"('{student.get('displayName')}', {student.get('points')}, {i}, '{json.dumps(exams)}', {isEGE}, {faculty_id}, {year}, '{student.get('passableProfile') or 'Нет профиля'}')")
    if arr:
        db, sql = create_connect(connect_data)
        sql.execute(f"""INSERT INTO students (id, points, contract_type, disciplines, isEGE, faculty_id, year, profile_name) VALUES {', '.join(arr)} ON CONFLICT DO NOTHING""")
        db.commit()
        db.close()
    return json.dumps({'message': 'Данные о поступивших студентах обновлены!', 'resultCode': 1}, ensure_ascii=False)


def getAllStudents():
    db, sql = create_connect(connect_data)
    sql.execute("SELECT id, year FROM faculties")
    faculties = sql.fetchall()
    for faculty in faculties:
        getStudents(*faculty)

    db.close()
    return json.dumps({'message': 'Данные о поступивших студентах обновлены!', 'resultCode': 1}, ensure_ascii=False)


if __name__ == '__main__':
    db, sql = create_connect(connect_data)
    sql.execute("""
        CREATE TABLE IF NOT EXISTS public.faculties
        (
            id integer,
            code text,
            title text,
            year integer,
            level integer,
            trainings integer,
            PRIMARY KEY (id)
        ) """)

    sql.execute("""CREATE TABLE IF NOT EXISTS institutes (
        profile_name text PRIMARY KEY,
        institute_id text,
        title text,
        institute_name text,
        group_name text
        )""")

    sql.execute("""CREATE TABLE IF NOT EXISTS students (
        id text,
        points integer,
        contract_type integer,
        disciplines jsonb,
        isEGE boolean,
        faculty_id integer,
        year integer,
        profile_name text,
        PRIMARY KEY(id),
        FOREIGN KEY (profile_name) REFERENCES institutes (profile_name) ON UPDATE RESTRICT ON DELETE RESTRICT
    )""")

    sql.execute("INSERT INTO institutes VALUES ('Нет профиля','spo','СПО','Среднее Профессиональное Образование','СПО') ON CONFLICT DO NOTHING")
    db.commit()
    db.close()

    updateFaculties()
    getAllStudents()

