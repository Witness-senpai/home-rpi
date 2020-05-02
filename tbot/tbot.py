import logging
import sys, os
from time import sleep

import telebot

sys.path.append(os.path.join(os.path.dirname(__file__), '../tools'))
from tools import get_teletoken

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

bot = telebot.TeleBot(get_teletoken())
telebot.apihelper.proxy = {'https': '200.195.162.242:3128'}
user_id = 0

def send_message(text):
    bot.send_message(
        user_id,
        text
)


@bot.message_handler(commands=['start'])
def entry_point(message):
    logger.info('kok')
    user_id = message.from_user.id
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("/status")
    bot.send_message(
        message.from_user.id, 
        "Это телеграм-бот домашней системы видеонаблюдения. " +
        "При обнаружении посторонних лиц в пределах камеры " +
        "бот сразу же пришлёт эти кадры в этот чат."
    )

@bot.message_handler(commands=['status'])
def status(message):
    logger.info('kok2')
    bot.send_message(
        message.from_user.id, 
        "Бот работает..."
    )

def main():
    bot.polling(none_stop=True, timeout=300)