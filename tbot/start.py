import logging 

from tbot.tbot import main

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

def bot_start(token):
    logger.info('Bot starting...')
    while True:
        try:
            main(token)
        except Exception as ex:
            logging.error(ex)
            exit()