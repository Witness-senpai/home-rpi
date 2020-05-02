import logging 

from tbot import main

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as ex:
            logging.error(ex)