import telebot
import app.config as config
import psycopg2
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
db = psycopg2.connect(**config.DB)
sql = db.cursor()

@bot.message_handler(commands=['start'])
def start(message):
    sql.execute(f'INSERT INTO users (id, is_admin) VALUES ({message.from_user.id}, false) ON CONFLICT DO NOTHING')
    db.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    markup.add(
        types.KeyboardButton(text='О нас'),
        types.KeyboardButton(text='Связаться с нами'),
        types.KeyboardButton(text='Стажировки'),
        types.KeyboardButton(text='FAQ'),
    )
    print(message.from_user)
    sql.execute(f"SELECT answer FROM questions WHERE type='start'")
    answer = sql.fetchone()
    bot.send_message(message.chat.id, text=answer[0], reply_markup=markup)


bot.infinity_polling()