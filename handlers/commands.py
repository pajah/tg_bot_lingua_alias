from random import choice

from telegram import Update

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext

from markups.rock_paper_scissors import menu, buttons
from models import User

from bot import bot

import logging

logger = logging.getLogger(__name__)


def start(update, ctx):
    u, is_created = User.get_or_create(
        tg_id=update.message.from_user.id,
        defaults={
            'username': update.message.from_user.first_name
        })
    logging.debug(u, is_created)
    msg = 'Hi, new user.' if is_created else 'Hi, old user.'
    ctx.bot.send_message(u.tg_id, msg, reply_markup=None)


def rock_paper_scissors(update, ctx):


    user_text = update._effective_message.text

    def generate_answer():
        return choice(['Rock', 'Paper', 'Scissors'])

    logger.warning(ctx._chat_data)

    if user_text == '/rock':
        msg = 'Start game. \n Type /stoprock to stop game.'
        logger.debug('Start game')
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=menu)
        ctx._chat_data.update({'rock_paper_scissors_started': True})
    elif user_text == '/stoprock':
        msg = 'Stop game'
        ctx.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=None)
        return
    else:
        user_ans = update._effective_message.text
        if user_ans in buttons:
            ans = generate_answer()
            msg = 'Your choice: %s \nMy choice: %s\n' % (user_ans, ans)
            if user_ans == ans:
                msg = msg + 'Same variants. Try again.'
            else:
                if (user_ans == 'Paper' and ans == 'Scissors') or (user_ans == 'Scissors' and ans == 'Rock') or (
                                user_ans == 'Rock' and ans == 'Paper'):
                        msg = msg + 'Bot win! Sasai)'
                        ctx.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=menu)
                else:
                    msg = msg + 'User win!'
                    ctx.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=menu)

        else:
            msg = 'Wrong choice.'
            ctx.bot.send_message(chat_id=update.effective_chat.id, text=msg, reply_markup=menu)


    logger.warning(update)
    # logger.warning('ctx chat data: %s ' % str(ctx._chat_data))
    # ctx._chat_data.update({'rock_paper_scissors_started': False})





