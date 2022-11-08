import datetime
from random import choices
import smtplib
from email.mime.multipart import MIMEMultipart
from . import app


def genCode(lenCode:int = 8):
    return ''.join(choices('1234567890qwertyuiopasdfgjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM', k=lenCode))

def get_timestamp(date=None) -> int:
    date = date or datetime.datetime.now()
    return int(''.join(str(date.timestamp()).split('.'))[0:13].ljust(13,'0'))

def logger(message:str):
    with open('request.log','w',encoding='utf-8') as f:
        f.write(message)

