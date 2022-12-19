import os
import re
import requests
import datetime
from os.path import join
from aiogram import Bot, types,Dispatcher
from app.config import TOKEN, host, cookies
from states import FormState, TicketState
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton,InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

START_MESSAGE = CONTACT_MESSAGE = FAQ_MESSAGE = FAQ_MESSAGES = MAIN_MARKUP = FORM_MESSAGE = TICKET_MESSAGE = {}

def check_date(date):
    try:
        d = datetime.datetime.strptime(date, '%d.%m.%Y')
    except ValueError:
        return False
    return d < datetime.datetime.now()

def gen_markup(data, _type) -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()

    for i in range(0, len(data), 2):
        row = data[i:i + 2]
        btns = [InlineKeyboardButton(text=row[0][1], callback_data=f'{_type}-' + str(row[0][0]))]

        if len(row) > 1:
            btns.append(InlineKeyboardButton(text=row[1][1], callback_data=f'{_type}-' + str(row[1][0])))

        keyboard.row(
            *btns
        )
    return keyboard


def get_messages():
    global START_MESSAGE, CONTACT_MESSAGE, FAQ_MESSAGE, FAQ_MARKUP, \
        FAQ_MESSAGES, MAIN_MARKUP, FORM_MESSAGE, TICKET_MESSAGE, PROFESSION_CODES, CITIES, DIRECTIONS, \
        education_markup, cities_markup, directions_markup


    START_MESSAGE = requests.get(f'{host}api/get-start-message', cookies=cookies).json()
    FORM_MESSAGE = requests.get(f'{host}api/get-form-message', cookies=cookies).json()
    TICKET_MESSAGE = requests.get(f'{host}api/get-ticket-message', cookies=cookies).json()
    CONTACT_MESSAGE = requests.get(f'{host}api/get-contacts-message', cookies=cookies).json()
    FAQ_MESSAGE = requests.get(f'{host}api/get-faq_main-message', cookies=cookies).json()
    FAQ_MESSAGES = requests.get(f'{host}api/get-faq-messages', cookies=cookies).json()
    EDUCATIONS = requests.get(f'{host}api/get-educations', cookies=cookies).json().get('data')
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
    education_markup = gen_markup(EDUCATIONS, 'education')
    cities_markup = gen_markup(CITIES, 'city')
    directions_markup = gen_markup(DIRECTIONS, 'direction')
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

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Подтверждаю', callback_data='approval'))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_form'))

    await bot.send_message(
        chat_id=event.from_user.id,
        text='Даю согласие на обработку данных\n<b><a href="https://dom.ginda.info/career/conditions">✅ Согласие</a></b>',
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(FormState.APPROVAL)

@dp.callback_query(lambda e: e.data and e.data == 'approval' and FormState.APPROVAL)
async def send_name(call,state):
    await bot.send_message(
        chat_id=call.from_user.id,
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

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Связаться', callback_data='create-ticket'))

    if TICKET_MESSAGE.get('attachment'):
        await bot.send_photo(
            chat_id=message.from_user.id,
            photo=get_static(TICKET_MESSAGE.get('attachment')),
            caption=text,
            reply_markup=keyboard.as_markup()
        )
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=keyboard.as_markup()

        )

@dp.callback_query(lambda call: call.data and call.data == 'create-ticket')
async def ticket_handler(call: types.Message, state):
    await state.set_state(TicketState.CREATE)
    await bot.send_message(
        chat_id=call.from_user.id,
        text='Введите сообщение, чтобы операторы могли вам помочь.'
    )

@dp.message( TicketState.CREATE )
async def create_ticket_handler(message: types.Message, state):
    profile_pictures = await bot.get_user_profile_photos(message.from_user.id, limit=1)
    file = await bot.get_file(profile_pictures.photos[0][-1].file_id)
    await bot.download_file(file.file_path, os.path.join('app','static','img','avatars', f'avatar_{message.from_user.id}.jpg'))

    await state.set_state(TicketState.ACTIVE)
    body = {
        'user':{
            'id':message.from_user.id,
            'name':message.from_user.username,
            'img': f'avatar_{message.from_user.id}.jpg',
        },
        'message':message.text
    }
    data = requests.post(f'{host}/create-ticket',json=body,cookies=cookies).json()
    await state.update_data(id=data.get("id","0"))

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=f'Закрыть тикет #{data.get("id","0")}', callback_data=f'close_ticket-{data.get("id")}'))

    await bot.send_message(
        chat_id=message.from_user.id,
        text='<b>Ищем свободных сотрудников.</b>\n<code>Ожидайте, скоро вам ответят!</code>',
        reply_markup=keyboard.as_markup()
    )


@dp.message(TicketState.ACTIVE, lambda m: m.text not in (FAQ_MESSAGE.get('title'), TICKET_MESSAGE.get('title'),FORM_MESSAGE.get('title'), CONTACT_MESSAGE.get('title')) )
async def create_ticket_message_handler(message: types.Message, state):
    ticket_id = await state.get_data()
    body = {
        'text':message.text,
        'name':message.from_user.username,
        'img':f'avatar_{message.from_user.id}.jpg',
        'user_id':message.from_user.id,
    }

    r = requests.post(f'{host}/tickets/{ticket_id.get("id")}', json=body, cookies=cookies)

    if r.status_code != 200:
        return

    r = r.json()
    if r.get('active') == False:
        await state.clear()

@dp.callback_query(lambda c: c.data and c.data.startswith('close_ticket-') and TicketState.ACTIVE)
async def close_ticket(call, state):
    ticket_id = call.data.replace('close_ticket-','')

    if not ticket_id.isdigit():
        return

    body = {
        'action':'close-ticket',
        'user_id':call.from_user.id
    }

    requests.post(f'{host}/tickets/{ticket_id}', json=body, cookies=cookies)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Вы отменили поиск.'
    )
    await state.clear()


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
    await state.update_data(name=message.text.title())

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите фамилию:'
    )


@dp.message(FormState.LAST_NAME_STATE)
async def get_last_name(message: types.Message, state):
    await state.set_state(FormState.FATHER_NAME_STATE)
    await state.update_data(surname=message.text.title())

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
    await state.update_data(father_name=message.text.title())

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите почту:'
    )


@dp.message(lambda m: m.text and re.fullmatch('^[^\s@]+@[a-z^\s@]+\.[a-z^\s@]+$', m.text) and FormState.EMAIL_STATE)
async def get_email(message: types.Message, state):

    await state.set_state(FormState.BIRTHDAY_STATE)
    await state.update_data(email=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Введите Дату рождения (31.01.2000):'
    )

@dp.message(FormState.EMAIL_STATE)
async def get_email_unknown(message: types.Message, state):

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Почта указана не корректно.'
    )

@dp.message(lambda m: m.text and check_date(m.text) and FormState.BIRTHDAY_STATE)
async def get_birthday_date(message: types.Message, state):

    await state.set_state(FormState.PROFESSION_STATE)

    await state.update_data(birthday_date=message.text)

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Направление образования:',
        reply_markup=education_markup.as_markup()
    )


@dp.message(FormState.BIRTHDAY_STATE)
async def get_birthday_date_unknown(message: types.Message):

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Такой даты не существует или она в будущем!'
    )

@dp.callback_query(lambda c: c.data and c.data.startswith('education-') and FormState.PROFESSION_STATE)
async def get_profession(call: types.Message, state):

    await state.set_state(FormState.UNIVERSITY_STATE)
    await state.update_data(profession_id=int(call.data.split('-')[-1]))

    await bot.send_message(
        chat_id=call.from_user.id,
        text='Введите название учебного заведения:'
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

    await bot.send_message(
        chat_id=message.from_user.id,
        text='Выберите город:',
        reply_markup=cities_markup.as_markup()
    )


@dp.callback_query( lambda e: e.data.startswith('city-') and FormState.CITY_STATE)
async def get_city(e, state):

    id = int(e.data[5:])

    await state.set_state(FormState.DIRECTION_STATE)
    await state.update_data(city_id=id)

    await bot.send_message(
        chat_id=e.from_user.id,
        text='Выберите направление стажировки:',
        reply_markup=directions_markup.as_markup()
    )


@dp.callback_query( lambda e: e.data.startswith('direction-') and FormState.DIRECTION_STATE)
async def get_direction(e, state):

    id = int(e.data[10:])
    await state.set_state(FormState.RESUME_STATE)
    await state.update_data(direction_id=id)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Без резюме', callback_data='skip_img'))

    await bot.send_message(
        chat_id=e.from_user.id,
        text='Пришлите своё резюме (файл):',
        reply_markup=keyboard.as_markup()
    )


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
        text='Проверьте данные анкеты и подтвердите отправку формы.',
        reply_markup=keyboard.as_markup()
    )

    await state.update_data(resume=file_name)


@dp.callback_query(lambda c: c.data and c.data=='skip_img' and FormState.RESUME_STATE)
async def get_file_skip(call, state):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Подтверждаю', callback_data='send_form'))
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='cancel_form'))

    await bot.send_message(
        chat_id=call.from_user.id,
        text='Проверьте данные анкеты и подтвердите отправку формы.',
        reply_markup=keyboard.as_markup()
    )

    await state.set_state(FormState.SUCCESS)
    await state.update_data(resume='')

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
    body['username'] = event.from_user.username
    await state.clear()
    requests.post(f'{host}api/form-handler', json=body, cookies=cookies)


if __name__ == '__main__':
    get_messages()
    dp.run_polling(bot)
