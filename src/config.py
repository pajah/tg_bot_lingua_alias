import os
from pathlib import Path

from peewee import SqliteDatabase


DB = SqliteDatabase('%s%sdatabase.db' % (Path(os.getcwd()).parent, os.sep))

DICTS_FOLDER = ('%s%sdicts' % (Path(os.getcwd()).parent, os.sep))

DEFAULT_TIMER = 30
MIN_TIMER_VALUE = 20
MAX_TIMER_VALUE = 300
DEFAULT_DICT_NAME = 'top_5000_eng_ru'
TOP_USERS_AMOUNT_TO_DISPLAY = 30

LINGUALEO_EMAIL = None
LINGUALEO_PASS = None
LINGUALEO_DYNAMIC_DICT_JSON = DICTS_FOLDER + '%sauthors_lingualeo_dynamic_dict_eng_ru.json' % os.sep


from config_local import *