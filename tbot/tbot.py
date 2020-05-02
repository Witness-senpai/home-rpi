import logging
from time import sleep

import telebot


logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

def main(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def entry_point(message):
        pass
     
    bot.polling(none_stop=True, timeout=60)