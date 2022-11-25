import os
import requests
from os.path import join
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from app.config import TOKEN, host, cookies
from aiogram.utils.markdown import escape_md
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

START_MESSAGE = CONTACT_MESSAGE = FAQ_MESSAGE = FAQ_MESSAGES = MAIN_MARKUP = FORM_MESSAGE = TICKET_MESSAGE = FAQ_TITLES = {}


def get_messages():
    global START_MESSAGE, CONTACT_MESSAGE, FAQ_MESSAGE, FAQ_MARKUP, FAQ_MESSAGES, MAIN_MARKUP, FORM_MESSAGE, TICKET_MESSAGE, FAQ_TITLES

    START_MESSAGE = requests.get(f'{host}api/get-start-message', cookies=cookies).json()
    FORM_MESSAGE = requests.get(f'{host}api/get-form-message', cookies=cookies).json()
    TICKET_MESSAGE = requests.get(f'{host}api/get-ticket-message', cookies=cookies).json()
    CONTACT_MESSAGE = requests.get(f'{host}api/get-contacts-message', cookies=cookies).json()
    FAQ_MESSAGE = requests.get(f'{host}api/get-faq_main-message', cookies=cookies).json()
    FAQ_MESSAGES = requests.get(f'{host}api/get-faq-messages', cookies=cookies).json()

    MAIN_MARKUP_ROWS = [FORM_MESSAGE, CONTACT_MESSAGE, FAQ_MESSAGE, TICKET_MESSAGE]

    MAIN_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
    FAQ_MARKUP = InlineKeyboardMarkup(row_width=2)
    FAQ_TITLES = {}

    for i, faq in enumerate(FAQ_MESSAGES):
        FAQ_TITLES[faq.get('id')] = faq.get('text')
        FAQ_MARKUP.add(InlineKeyboardButton(faq.get('title'), callback_data=i))

    for button in MAIN_MARKUP_ROWS:
        print(button, button.get('title'))
        MAIN_MARKUP.add(button.get('title'))

    print('BUTTONS LOADED')

get_messages()

def get_static(file_name:str) -> str:
    f = open(join(os.getcwd(), 'app', 'static', 'message', file_name), 'rb')
    data = f.read()
    f.close()
    return data

@dp.message_handler(commands=['refresh_buttons'])
async def refresh_buttons(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text='Перезагружаю...'
    )

    get_messages()

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Перезагрузил кнопки!'
    )

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):

    text = START_MESSAGE.get('text')
    if START_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(START_MESSAGE.get('attachment')),
            caption=text,
            reply_markup=MAIN_MARKUP,
            parse_mode=types.ParseMode.HTML
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=MAIN_MARKUP,
            parse_mode=types.ParseMode.HTML
        )

    requests.get(f'{host}api/add-use-{message.from_user.id}', cookies=cookies)

@dp.message_handler(lambda message: CONTACT_MESSAGE.get('title') == message.text)
async def contact_handler(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=CONTACT_MESSAGE.get('text'),
        parse_mode=types.ParseMode.HTML
    )

@dp.message_handler(lambda message: FAQ_MESSAGE.get('title') == message.text)
async def faq_main_handler(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=FAQ_MESSAGE.get('text'),
        parse_mode=types.ParseMode.HTML,
        reply_markup=FAQ_MARKUP
    )

@dp.message_handler(lambda message: TICKET_MESSAGE.get('title') == message.text)
async def ticket_handler(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=TICKET_MESSAGE.get('text'),
        parse_mode=types.ParseMode.HTML,
        reply_markup=FAQ_MARKUP
    )

@dp.callback_query_handler(lambda call: call.data and call.data.isdigit() and int(call.data) < len(FAQ_TITLES))
async def faq_handler(call: types.Message):
    data = FAQ_MESSAGES[int(call.data)]
    text = data.get('text')
    if data.get('attachment'):
        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=get_static(data.get('attachment')),
            caption=text,
            parse_mode=types.ParseMode.HTML
        )
    else:
        await bot.send_message(
            chat_id=call.from_user.id,
            text=text,
            parse_mode=types.ParseMode.HTML
        )



if __name__ == '__main__':
    executor.start_polling(dp)