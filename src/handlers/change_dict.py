from telegram.ext import ConversationHandler
from telegram import parsemode

# from .commands import start, cancel, utils
from markups.change_dict_menu import make_change_dict_menu
# from markups.fuel_menu import fuel_start_menu, fuel_show_menu, make_edit_fuel_menu
# from markups.start_menu import start_menu_logined
# from markups import utils_menu
from models import GameRoom

from config import DEFAULT_DICT_NAME, DICTS_FOLDER

import os
import logging

from pathlib import Path
from handlers.admin_settings import _check_if_user_is_admin


# from dicts import *

logger = logging.getLogger(__name__)

DICT_LIST, DICT_SET, DICT_DONE = map(chr, range(3))


def _set_dictionary(chat_id, dict_name=DEFAULT_DICT_NAME):
    logger.warning('Trying to set dict with name: %s' % dict_name)
    game_room = GameRoom.get(tg_id=chat_id)
    if game_room.dictionary_name != dict_name:
        game_room.dictionary_name = dict_name
        game_room.save()


def display_dict_list(upd, ctx):
	
	chat_id = upd.effective_chat.id
	if _check_if_user_is_admin(upd, ctx):
		ctx.chat_data['settings'] = {}
		# path = Path(os.path.abspath(__file__))
		# logger.warning(path)
		dicts = []
		for filename in os.listdir(DICTS_FOLDER):
			f = os.path.join(DICTS_FOLDER, filename)
			if os.path.isfile(f):
				# print(f)
				# logger.warning(filename)
				if '.json' in filename:
					dicts.append(filename.replace('.json', ''))

		if 'settings' in ctx.chat_data and 'dict_name' in ctx.chat_data['settings']:
			current_dict = ctx.chat_data['settings']['dict_name']
		else:
			current_dict = GameRoom.get(tg_id=chat_id).dictionary_name
			ctx.chat_data['settings']['dict_name'] = current_dict

		msg = 'Now your dict is: <b>%s</b>\n'\
			  'Please reply with nubmer of dict which is needed to be set\n'\
			  '(like <b>0</b> or <b>1</b>)\n' % current_dict
		for number, dict_name in enumerate(dicts):
			# logger.warning()
			# for number, dict_name in enumerate(d):
			logger.warning('%s: %s' % (number, dict_name))
			msg += '<b>%s</b>: %s\n' % (number, dict_name)
		ctx.chat_data['settings']['available_dicts'] = dicts
		upd.message.reply_text(msg, parse_mode=parsemode.ParseMode.HTML)
		return DICT_SET
	
	else:  # not chat admin
		reply_text = 'Sorry, you are not in chat admins list.\n'
		ctx.bot.send_message(chat_id=chat_id,
						 	 reply_to_message_id=upd.message.message_id,
						 	 text=reply_text)


def dict_set(upd, ctx):
	chat_id = upd.effective_chat.id
	usert_dict_nubmer_input = upd.message.text
	try:
		number_of_needed_dict = int(usert_dict_nubmer_input)
		assert(number_of_needed_dict < len(ctx.chat_data['settings']['available_dicts']))
	except ValueError:
		upd.message.reply_text('Only nubmers allower. Retry please.')
		return DICT_SET
	except AssertionError:
		upd.message.reply_text('Wrong nubmer. Retry.')
		return DICT_SET
	ctx.chat_data['settings']['user_dict_choise'] = usert_dict_nubmer_input

	if 'settings' not in ctx.chat_data:
		ctx.chat_data['settings'] = {}


	# valid choise
	logger.warning('Trying to set dictionary with user choise %s that is %s' % 
				   (ctx.chat_data['settings']['user_dict_choise'],
				   	ctx.chat_data['settings']['available_dicts'][number_of_needed_dict]))
	
	needed_dict_name = ctx.chat_data['settings']['available_dicts'][number_of_needed_dict]

	logger.critical(needed_dict_name)
	logger.critical(ctx.chat_data['settings']['dict_name'])

	# needed dict is alrealy chosen
	if 'dict_name' in ctx.chat_data['settings']:
		if ctx.chat_data['settings']['dict_name'] == needed_dict_name:
			msg = 'Chosen dict is already set!\nCancelling.'
			upd.message.reply_text(msg)
			ctx.chat_data['settings']['user_dict_choise'] = None
			ctx.chat_data['settings']['available_dicts'][number_of_needed_dict] = None
			
			return ConversationHandler.END

	# success flow
	_set_dictionary(chat_id=upd.effective_chat.id, dict_name=needed_dict_name)
	ctx.chat_data['settings']['dict_name'] = needed_dict_name

	msg = 'New dictionary has set: %s ' % needed_dict_name
	
	upd.message.reply_text(msg)

	ctx.chat_data['settings']['user_dict_choise'] = None
	ctx.chat_data['settings']['available_dicts'][number_of_needed_dict] = None

	return ConversationHandler.END



# # def set_dict(upd, ctx):




# if __name__ == '__main__':
#     llist()
