import os
import requests
from os.path import join
from aiogram import Bot, types,Dispatcher
from app.config import TOKEN, host, cookies
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton,InlineKeyboardBuilder

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

START_MESSAGE = CONTACT_MESSAGE = FAQ_MESSAGE = FAQ_MESSAGES = MAIN_MARKUP = FORM_MESSAGE = TICKET_MESSAGE = {}


def get_messages():
    global START_MESSAGE, CONTACT_MESSAGE, FAQ_MESSAGE, FAQ_MARKUP, FAQ_MESSAGES, MAIN_MARKUP, FORM_MESSAGE, TICKET_MESSAGE

    START_MESSAGE = requests.get(f'{host}api/get-start-message', cookies=cookies).json()
    FORM_MESSAGE = requests.get(f'{host}api/get-form-message', cookies=cookies).json()
    TICKET_MESSAGE = requests.get(f'{host}api/get-ticket-message', cookies=cookies).json()
    CONTACT_MESSAGE = requests.get(f'{host}api/get-contacts-message', cookies=cookies).json()
    FAQ_MESSAGE = requests.get(f'{host}api/get-faq_main-message', cookies=cookies).json()
    FAQ_MESSAGES = requests.get(f'{host}api/get-faq-messages', cookies=cookies).json()

    MAIN_MARKUP_ROWS = [(FORM_MESSAGE, CONTACT_MESSAGE), (FAQ_MESSAGE, TICKET_MESSAGE)]

    MAIN_MARKUP = ReplyKeyboardBuilder()
    FAQ_MARKUP = InlineKeyboardBuilder()

    buttons = []

    for i, faq in enumerate(FAQ_MESSAGES):
       buttons.append(InlineKeyboardButton(text=faq.get('title'), callback_data=i))

    FAQ_MARKUP.row(*buttons, width=2)

    for button in MAIN_MARKUP_ROWS:
        MAIN_MARKUP.row(
            KeyboardButton(text=button[0].get('title')),
            KeyboardButton(text=button[1].get('title'))
        )

    MAIN_MARKUP = MAIN_MARKUP.as_markup(resize_keyboard=True)
    FAQ_MARKUP = FAQ_MARKUP.as_markup()
    print('BUTTONS LOADED')


get_messages()


def get_static(file_name:str) -> str:
    f = open(join(os.getcwd(), 'app', 'static', 'message', file_name), 'rb')
    data = f.read()
    f.close()
    return data


@dp.message(commands=['refresh_buttons'])
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


@dp.message(commands=['start'])
async def process_start_command(message: types.Message):

    text = START_MESSAGE.get('text')
    if START_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(START_MESSAGE.get('attachment')),
            caption=text,
            reply_markup=MAIN_MARKUP
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=MAIN_MARKUP
        )
    requests.get(f'{host}api/add-use-{message.from_user.id}', cookies=cookies)


@dp.message(lambda message: CONTACT_MESSAGE.get('title') == message.text)
async def contact_handler(message: types.Message):

    await bot.send_message(
        chat_id=message.from_user.id,
        text=CONTACT_MESSAGE.get('text')
    )


@dp.message(lambda message: FORM_MESSAGE.get('title') == message.text)
async def form_handler(message: types.Message):

    await bot.send_message(
        chat_id=message.from_user.id,
        text=FORM_MESSAGE.get('text')
    )


@dp.message(lambda message: FAQ_MESSAGE.get('title') == message.text)
async def faq_main_handler(message: types.Message):

    await bot.send_message(
        chat_id=message.from_user.id,
        text=FAQ_MESSAGE.get('text'),
        reply_markup=FAQ_MARKUP
    )

@dp.message(lambda message: TICKET_MESSAGE.get('title') == message.text)
async def ticket_handler(message: types.Message):

    await bot.send_message(
        chat_id=message.from_user.id,
        text=TICKET_MESSAGE.get('text')
    )

@dp.callback_query(lambda call: call.data and call.data.isdigit() and int(call.data) < len(FAQ_MESSAGES))
async def faq_handler(call: types.Message):

    data = FAQ_MESSAGES[int(call.data)]
    text = data.get('text')

    if data.get('attachment'):
        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=get_static(data.get('attachment')),
            caption=text
        )
    else:
        await bot.send_message(
            chat_id=call.from_user.id,
            text=text
        )


if __name__ == '__main__':
    dp.run_polling(bot)
