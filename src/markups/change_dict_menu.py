from telegram import ReplyKeyboardMarkup, KeyboardButton

# button = KeyboardButton(text='Test but', )

# fuel_menu_buttons = ['/log', '/list']
# fuel_show_buttons = ['/log', '/list', '/show']

# fuel_start_menu = ReplyKeyboardMarkup([fuel_menu_buttons])
# fuel_show_menu = ReplyKeyboardMarkup([fuel_show_buttons])

import logging


logger = logging.getLogger(__name__)



def make_change_dict_menu(dicts_enumerated):
    buttons = []
    for number, dict_name in dicts_enumerated:
        button = '/%s' % number
        buttons.append([button])
    logger.warning(str(buttons))
    return ReplyKeyboardMarkup(buttons)


# fuel_start_menu = ReplyKeyboardMarkup([fuel_menu_buttons])