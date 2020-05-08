import logging
import sys, os
from time import sleep

import telebot

sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))
from tools import (
    get_teletoken,
    add_user_to_settings,
    load_settings,
    change_settings,
    set_trigger_flag,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

bot = telebot.TeleBot(get_teletoken())
telebot.apihelper.proxy = {'https': '200.195.162.242:3128'}
user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
user_markup.row("/add", "/status", "/OK")

def send_message(text, photo):
    users = load_settings()['telegram_users']
    for user_id in users:
        bot.send_message(user_id, text)
        bot.send_photo(user_id, photo)
        bot.send_message(user_id, "Флаг обнаружения сброшен. \
            Пришлите команду /OK, чтобы выставить его.")

@bot.message_handler(commands=['start'])
def entry_point(message):
    bot.send_message(
        message.from_user.id, 
        "Это телеграм-бот домашней системы видеонаблюдения. " +
        "При обнаружении посторонних лиц в пределах камеры " +
        "бот сразу же пришлёт эти кадры в этот чат.",
        reply_markup=user_markup
    )

@bot.message_handler(commands=['status'])
def status(message):
    bot.send_message(
        message.from_user.id, 
        "Бот работает...",
        reply_markup=user_markup
    )

@bot.message_handler(commands=['add'])
def add_user(message):
    add_user_to_settings(message.from_user.id)
    change_settings('telebot_username', eval(str(bot.get_me()))['username'])
    bot.send_message(
        message.from_user.id, 
        "Я запомнил вас и в случае чего вы получите оповещение.",
        reply_markup=user_markup
    )

@bot.message_handler(commands=['OK'])
def status(message):
    bot.send_message(
        message.from_user.id, 
        "Флаг обнаружения выставлен.",
        reply_markup=user_markup
    )
    set_trigger_flag()

@bot.message_handler(content_types=['text'])
def calcAnyText(message):
    bot.send_message(
        message.from_user.id, 
        "Чтобы запомнил ваш чат для рассылки введите /add." + 
        "Чтобы проверить статус боту введите /status",
        reply_markup=user_markup
    )

def main():
    bot.polling(none_stop=True, timeout=300)