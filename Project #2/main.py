import os
import re
import requests
from os.path import join
from aiogram import Bot, types,Dispatcher
from app.config import TOKEN, host, cookies
from form_state import FormState, form_router
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton,InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

START_MESSAGE = CONTACT_MESSAGE = FAQ_MESSAGE = FAQ_MESSAGES = MAIN_MARKUP = FORM_MESSAGE = TICKET_MESSAGE = {}


def get_messages():
    global START_MESSAGE, CONTACT_MESSAGE, FAQ_MESSAGE, FAQ_MARKUP, \
        FAQ_MESSAGES, MAIN_MARKUP, FORM_MESSAGE, TICKET_MESSAGE, PROFESSION_CODES, CITIES, DIRECTIONS

    START_MESSAGE = requests.get(f'{host}api/get-start-message', cookies=cookies).json()
    FORM_MESSAGE = requests.get(f'{host}api/get-form-message', cookies=cookies).json()
    TICKET_MESSAGE = requests.get(f'{host}api/get-ticket-message', cookies=cookies).json()
    CONTACT_MESSAGE = requests.get(f'{host}api/get-contacts-message', cookies=cookies).json()
    FAQ_MESSAGE = requests.get(f'{host}api/get-faq_main-message', cookies=cookies).json()
    FAQ_MESSAGES = requests.get(f'{host}api/get-faq-messages', cookies=cookies).json()
    PROFESSIONS = requests.get(f'{host}api/get-profession_codes', cookies=cookies).json().get('data')
    CITIES = requests.get(f'{host}api/get-cities', cookies=cookies).json().get('data')
    DIRECTIONS = requests.get(f'{host}api/get-directions', cookies=cookies).json().get('data')

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

    PROFESSION_CODES = {code:id for id, code, _ in PROFESSIONS}
    print('BUTTONS LOADED')


def get_static(file_name:str) -> str:
    return FSInputFile(path=join(os.getcwd(), 'app', 'static', 'message', file_name))


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

    text = CONTACT_MESSAGE.get('text')

    if CONTACT_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(CONTACT_MESSAGE.get('attachment')),
            caption=text
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text
        )


@dp.message(lambda message: FORM_MESSAGE.get('title', 'Стажировки') == message.text)
async def form_handler(message: types.Message, state):
    text = FORM_MESSAGE.get('text')
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Заполнить анкету!', callback_data='create_form'))

    if FORM_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(FORM_MESSAGE.get('attachment')),
            caption=text,
            reply_markup=keyboard.as_markup()
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=keyboard.as_markup()
        )


@dp.callback_query(lambda e:e.data and e.data == 'create_form')
async def create_form(event, state):

    await bot.send_message(
        chat_id=event.from_user.id,
        text="Введите имя:"
    )
    await state.set_state(FormState.FIRST_NAME_STATE)


@dp.message(lambda message: FAQ_MESSAGE.get('title') == message.text)
async def faq_main_handler(message: types.Message):

    text = FAQ_MESSAGE.get('text')

    if FAQ_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(FAQ_MESSAGE.get('attachment')),
            caption=text,
            reply_markup=FAQ_MARKUP
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=FAQ_MARKUP
        )


@dp.message(lambda message: TICKET_MESSAGE.get('title') == message.text)
async def ticket_handler(message: types.Message):

    text = TICKET_MESSAGE.get('text')

    if TICKET_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(TICKET_MESSAGE.get('attachment')),
            caption=text
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text
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


@dp.message(FormState.FIRST_NAME_STATE)
async def get_first_name(message: types.Message, state):
    await state.set_state(FormState.LAST_NAME_STATE)
    await state.update_data(name=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите фамилию:'
    )


@dp.message(FormState.LAST_NAME_STATE)
async def get_last_name(message: types.Message, state):
    await state.set_state(FormState.FATHER_NAME_STATE)
    await state.update_data(surname=message.text)

    no_father_name = InlineKeyboardBuilder()
    no_father_name.row(InlineKeyboardButton(text='Отсутствует', callback_data='no_father_name'))

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите отчество:',
        reply_markup=no_father_name.as_markup()
    )


@dp.callback_query(lambda e: e.data == 'no_father_name' and FormState.FATHER_NAME_STATE)
async def get_father_callback(call, state):

    await state.set_state(FormState.EMAIL_STATE)
    await state.update_data(father_name='')

    await bot.send_message(
        chat_id=call.from_user.id,
        text='Введите почту:'
    )


@dp.message(FormState.FATHER_NAME_STATE)
async def get_father_callback(message: types.Message, state):

    await state.set_state(FormState.EMAIL_STATE)
    await state.update_data(father_name=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите почту:'
    )


@dp.message(FormState.EMAIL_STATE)
async def get_email(message: types.Message, state):

    await state.set_state(FormState.BIRTHDAY_STATE)
    await state.update_data(email=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите Дату рождения (31.01.2000):'
    )


@dp.message(lambda m: m.text and re.fullmatch('[0-3]\d.[0-1]\d.[1-2][0,9]\d\d', m.text) and FormState.BIRTHDAY_STATE)
async def get_birthday_date(message: types.Message, state):

    await state.set_state(FormState.PROFESSION_STATE)
    await state.update_data(birthday_date=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите код специальности (09.03.01):'
    )


@dp.message(lambda m: m.text and re.fullmatch('\d\d.\d\d.\d\d', m.text) and m.text in PROFESSION_CODES and FormState.PROFESSION_STATE)
async def get_profession(message: types.Message, state):

    await state.set_state(FormState.UNIVERSITY_STATE)
    await state.update_data(profession_id=PROFESSION_CODES[message.text])

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите название университета:'
    )


@dp.message(FormState.UNIVERSITY_STATE)
async def get_university(message: types.Message, state):

    await state.set_state(FormState.COVER_LETTER_STATE)
    await state.update_data(university=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите сопроводительное письмо:'
    )


@dp.message(FormState.COVER_LETTER_STATE)
async def get_cover_letter(message: types.Message, state):

    await state.set_state(FormState.CITY_STATE)
    await state.update_data(cover_letter=message.text)

    cities_keyboard = InlineKeyboardBuilder()

    for id,city in CITIES:
        cities_keyboard.add(InlineKeyboardButton(text=city, callback_data='city-'+str(id)))

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Выберите город:',
        reply_markup=cities_keyboard.as_markup()
    )


@dp.callback_query( lambda e: e.data.startswith('city-') and FormState.CITY_STATE)
async def get_city(e, state):

    id = int(e.data[5:])

    await state.set_state(FormState.DIRECTION_STATE)
    await state.update_data(city_id=id)

    direction_keyboard = InlineKeyboardBuilder()

    for id, name in DIRECTIONS:
        direction_keyboard.add(InlineKeyboardButton(text=name, callback_data='direction-' + str(id)))

    await bot.send_message(
        chat_id=e.from_user.id,
        text='Выберите направление стажировки:',
        reply_markup=direction_keyboard.as_markup()
    )


@dp.callback_query( lambda e: e.data.startswith('direction-') and FormState.DIRECTION_STATE)
async def get_direction(e, state):

    id = int(e.data[10:])
    await state.set_state(FormState.RESUME_STATE)
    await state.update_data(direction_id=id)

    direction_keyboard = InlineKeyboardBuilder()

    for id, name in DIRECTIONS:
        direction_keyboard.add(InlineKeyboardButton(text=name, callback_data='direction-' + str(id)))

    await bot.send_message(
        chat_id=e.from_user.id,
        text='Пришлите свооё резюме (файл):'
    )
    d = await state.get_data()


@dp.message(lambda m: (m.photo or m.document) and FormState.RESUME_STATE)
async def get_file(m, state):

    await state.set_state(FormState.SUCCESS)

    end_name = ''

    if m.photo:
        end_name = '.jpg'
        file = m.photo[-1]
    elif m.document:
        end_name = m.document.file_name.split('.')[-1]
        file = m.document

    file_name = f"{file.file_id}.{end_name}"

    await bot.download(
        file,
        destination=os.path.join('app','static','img','resume',file_name)
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Подтверждаю', callback_data='send_form'))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_form'))

    await bot.send_message(
        chat_id=m.from_user.id,
        text='Даю согласие на обработку данных\n<b><a href="https://дом.рф/career/internship/#conditions">✅ Согласие</a></b>',
        reply_markup=keyboard.as_markup()
    )

    await state.update_data(resume=file_name)


@dp.callback_query(lambda e: e.data == 'cancel_form' and FormState.SUCCESS)
async def close_form(event, state):
    await bot.send_message(
        chat_id=event.from_user.id,
        text='Вы вернулись в меню!',
        reply_markup=MAIN_MARKUP
    )
    await state.clear()


@dp.callback_query(lambda e: e.data == 'send_form' and FormState.SUCCESS)
async def send_form(event, state):
    await bot.send_message(
        chat_id=event.from_user.id,
        text='Анкета отправлена!',
        reply_markup=MAIN_MARKUP
    )
    body = await state.get_data()
    body['user_id'] = event.from_user.id
    await state.clear()
    requests.post(f'{host}api/form-handler', json=body, cookies=cookies)


if __name__ == '__main__':
    get_messages()
    dp.run_polling(bot)
