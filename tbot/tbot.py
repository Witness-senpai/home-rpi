import telebot
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

TOKEN = '123'

def main():
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
        pass
     
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as ex:
        logging.error(ex)  