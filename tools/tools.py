import json
import logging
from shutil import copyfile

DEFAULT_SETTINGS_PATH = 'database/settings/default_settings.json'
SETTINGS_PATH = 'database/settings/settings.json'

logger = logging.getLogger(__name__)
logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)s: %(module)s: %(message)s')


def save_settings(json_settings):
    with open(SETTINGS_PATH, 'w') as json_file:
        json.dump(json_settings, json_file)

def load_settings():
    with open(SETTINGS_PATH) as json_file:
        return json.load(json_file)

def to_default():
    """
    Copy default settings to current settings file
    """
    try:
        copyfile(DEFAULT_SETTINGS_PATH, SETTINGS_PATH)
    except Exception as ex:
        logger.error(ex)
    else:
        logger.info('Copy default setting to current settings.')

<<<<<<< HEAD
data = {
    'telegram_token': 'U4JF7SMF8GDJ',
    'resolution': '1280x960',
    'orientation': '0',
    'recognition_status': 'True',
    'isdetect': ['2', '3']
}
to_default()
save_settings(data)

=======
>>>>>>> master
