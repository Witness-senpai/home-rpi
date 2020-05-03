import json
import logging
from shutil import copyfile

from numpy import array
from PIL.Image import open as pil_open

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

def get_teletoken():
    return load_settings()['telegram_token']

def change_settings(key, value):
    """
    Change settings dict by key and value
    """
    settings = load_settings()
    settings[key] = value
    save_settings(settings)

def add_user_to_settings(user):
    settings = load_settings()
    if user not in settings['telegram_users']:
        settings['telegram_users'].append(user)
    save_settings(settings)