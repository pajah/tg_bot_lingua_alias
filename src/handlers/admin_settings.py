from telegram.ext import ConversationHandler

# from .commands import start, cancel, utils
from markups.change_dict_menu import make_change_dict_menu
# from markups.fuel_menu import fuel_start_menu, fuel_show_menu, make_edit_fuel_menu
# from markups.start_menu import start_menu_logined
# from markups import utils_menu
# import GameRoom
from models import User, GameRoom

from config import DEFAULT_DICT_NAME, DICTS_FOLDER, MIN_TIMER_VALUE, MAX_TIMER_VALUE

import os
import logging

from pathlib import Path

# from dicts import *

logger = logging.getLogger(__name__)

# DICT_LIST, DICT_SET, DICT_DONE = map(chr, range(3))

SET_SETTINGS, SET_AUTOSTART, SET_TIMER, SET_DICT = map(chr, range(4))


def _check_if_user_is_admin(upd, ctx):

	user_id = upd.message.from_user.id
	chat_id = upd.effective_chat.id
	admin_tg_ids = [u.user.id for u in ctx.bot.get_chat_administrators(chat_id)]

	if user_id not in admin_tg_ids:
		return False
	else:  # admin case
		return True

def set_admin_settings(upd, ctx):
    chat_id = upd.effective_chat.id
    if _check_if_user_is_admin(upd, ctx):
    	reply_text = '/set_autostart — change on/off new game after win or loose (chat admin only)\n'\
        			 '/set_timer 30 — change time limit for answer in seconds (chat admin only)\n'\
        			 '/set_dict — change dictionary (chat admin only)\n'
    else:
    	reply_text = 'Sorry, you are not in chat admins list.\n'
    ctx.bot.send_message(chat_id=chat_id,
    					 reply_to_message_id=upd.message.message_id,
    					 text=reply_text)


def set_autostart(upd, ctx):
    """Checks admin permissions and enables or disables autostart for current Gameroom."""
    user_id = upd.message.from_user.id
    chat_id = upd.effective_chat.id
    reply_text = ''

    admin_tg_ids = [u.user.id for u in ctx.bot.get_chat_administrators(chat_id)]

    if user_id not in admin_tg_ids:
        reply_text += 'Sorry, you are not in chat admins list.\n'

    else:  # admin case
        game_room = GameRoom.get(tg_id=chat_id)

        if game_room.autostart:
            game_room.autostart = False
            game_room.save()
            ctx.chat_data['autostart'] = False
            reply_text = 'Game autostart has been disabled.'

        else:
            game_room.autostart = True
            game_room.save()
            ctx.chat_data['autostart'] = True
            reply_text = 'Game autostart has been enabled.'


    ctx.bot.send_message(chat_id=chat_id, reply_to_message_id=upd.message.message_id, text=reply_text)


def set_timer(upd, ctx):
    """Checks admin permissions and sets a timer for wait before announce the right answer (in seconds)."""
    user_id = upd.message.from_user.id
    chat_id = upd.effective_chat.id
    reply_text = ''

    admin_tg_ids = [u.user.id for u in ctx.bot.get_chat_administrators(chat_id)]

    if user_id not in admin_tg_ids:
        reply_text += 'Sorry, you are not in chat admins list.\n'
        ctx.bot.send_message(chat_id=chat_id,
                             reply_to_message_id=upd.message.message_id,
                             text=reply_text)
    else:  # admin case
        message_text = upd.message.text
        args = message_text.strip().split(' ')
        if len(args) == 2:
            if int(args[1]):
                timer = int(args[1])
                if MIN_TIMER_VALUE <= timer <= MAX_TIMER_VALUE:  # timer ok
                    gameroom, room_is_created = GameRoom.get_or_create(tg_id=chat_id)
                    gameroom.timer = timer
                    gameroom.save()
                    if 'settings' not in ctx.chat_data:
                        ctx.chat_data['settings'] = {}
                    
                    ctx.chat_data['settings']['timer'] = timer

                    reply_text = 'Timer %s seconds has been set successfully.\n' % timer
                    ctx.bot.send_message(chat_id=chat_id,
                                         reply_to_message_id=upd.message.message_id,
                                         text=reply_text)

                else:  # wrong limits
                    reply_text = 'Allowed timer is between %s and %s seconds. \n' % (MIN_TIMER_VALUE, MAX_TIMER_VALUE)
                    ctx.bot.send_message(chat_id=chat_id,
                                         reply_to_message_id=upd.message.message_id,
                                         text=reply_text)
        else:  # wrong format
            reply_text = 'Wrong format. Use: \n' \
                         '"/set_timer %s-%s"\n' % (MIN_TIMER_VALUE, MAX_TIMER_VALUE)
            ctx.bot.send_message(chat_id=chat_id,
                                 reply_to_message_id=upd.message.message_id,
                                 text=reply_text)
            print('Wrong format')
