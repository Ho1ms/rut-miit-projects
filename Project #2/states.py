from aiogram.dispatcher.fsm.state import State, StatesGroup

class FormState(StatesGroup):

    APPROVAL = State()
    FIRST_NAME_STATE = State()
    LAST_NAME_STATE = State()
    FATHER_NAME_STATE = State()
    BIRTHDAY_STATE = State()
    CITY_STATE = State()
    DIRECTION_STATE = State()
    EMAIL_STATE = State()
    COVER_LETTER_STATE = State()
    UNIVERSITY_STATE = State()
    PROFESSION_STATE = State()
    RESUME_STATE = State()
    SUCCESS = State()

class TicketState(StatesGroup):

    CREATE = State()
    ACTIVE = State()

