from string import ascii_lowercase

from random import choice
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardRemove, Message, Chat

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext
from telegram import parsemode

from markups.start_menu import start_menu
# from markups.utils_menu import utils_menu, utils_menu_buttons
from models import User, GameRoom, UserRoomScore  #, Game, 

from test_dictionary import TEST_ENG_RU_DICTIONARY_5000, DEFAULT_ENG_RU_DICTIONARY

from bot import bot

from config import BOT_NAME, DEFAULT_TIMER, DEFAULT_DICT_NAME, TOP_USERS_AMOUNT_TO_DISPLAY, DICTS_FOLDER

import os
import logging
import time
import json


logger = logging.getLogger(__name__)


def display_help(upd, ctx):
    """Displays help for user."""
    reply_text = '<b>Commands:</b>\n' \
                    '/help — show this help\n'\
                    '/start — start new game\n'\
                    '/stop — stop current game\n'\
                    '/info — get game settings TBD\n'\
                    '/score — show your points amount\n'\
                    '/top — show chat leaders\n'\
                    '/settings — set game settings (chat admin only)\n'

    ctx.bot.send_message(chat_id=upd.effective_chat.id, text=reply_text,
                         parse_mode=parsemode.ParseMode.HTML,
                         reply_markup=ReplyKeyboardRemove())


def _mask_string(world):
    """Hides given string with * except some of symbols."""
    mask = ''
    for s in world:
        if s.isalpha():  # hide
            mask += '*'
        if s in (' ', ',', '(', ')', '-'):  # don't hide
            mask += s
    return mask


def _send_answer_to_chat(ctx):
    """Sends right answer to chat and griggers new round if Gameroom autostart was enabled."""
    job = ctx.job
    answer = job.context.get('answer')
    riddle = job.context.get('riddle')
    chat_id = job.context.get('chat_id')
    right_anwer_text = '<b>Loosers!</b>\n' \
                       'Noone guessed the translation: \n' \
                       '<pre>%s</pre> = <pre>%s</pre>' % (riddle, answer)

    ctx.bot.send_message(chat_id=chat_id, text=right_anwer_text,
                         parse_mode=parsemode.ParseMode.HTML)

    if not 'timer' in job.context:
        logger.warning('No timer when answer to chat!')
    if job.context.get('autostart'):
        timer = job.context.get('timer')
        logger.critical('Timer before autostart new round: %s' % timer)

        logger.critical('Upd orig: %s' % str(job.context.get('original_update')))
        logger.critical('Ctx orig: %s' % str(job.context.get('original_context').chat_data))
        _start_new_round(upd=job.context.get('original_update'), ctx=job.context.get('original_context'), timer=timer)


def check_for_bot_abuse(upd, ctx):
    """Responses stupidly when bot was mentioned in chat."""
    logger.debug(str(upd.message))
    variants = ()
    if 'text' in upd.message:
        message_text = upd.message.text
        if message_text.strip().split(' ')[0] == BOT_NAME:
            # print(message_text.lower().strip().split(' ')[1])
            if message_text.lower().strip().split(' ')[1] in ('ты', 'you\'re'):
                ctx.bot.send_message(chat_id=upd.effective_chat.id, reply_to_message_id=upd.message.message_id,
                                     text='Кто как обзывается — тот так и называется!')
    else:
        return


def check_user_message_for_answer(upd, ctx):
    """
    Checks users messages for right answer if amount of words in message equals to amount in riddle.
    Updated user statistic and start new round if autostart was enabled.
    """

    logger.debug('!!! '+ str(ctx.chat_data))

    if not ctx.chat_data.get('active_game'):
        logger.warning('No active game!')
        return

    # print(upd.message)
    user_id = upd.message.from_user.id
    chat_id = upd.effective_chat.id
    message_text = upd.message.text

    # print(ctx.chat_data)

    # print(upd.effective_chat)

    logger.debug('!!! '+ str(ctx.chat_data))

    if 'active_game' in ctx.chat_data and 'answer' in ctx.chat_data['active_game']:

        logger.debug('HERE!')

        if len(message_text.strip().split(' ')) == len(ctx.chat_data.get('active_game').get('answer').split(' ')):
            
            # answer is correct
            if message_text.lower().strip() == ctx.chat_data.get('active_game').get('answer').lower().strip():

                # remove answer announce
                current_jobs = ctx.job_queue.jobs()
                for job in current_jobs:
                    if job.context['chat_id'] == chat_id:
                        job.schedule_removal()

                # get winner info
                user, user_is_created = User.get_or_create(
                    tg_id=user_id,
                    defaults={
                        'username': upd.message.from_user.first_name
                    })
                if user:
                    u = User.update(score=User.score + 1).where(User.id == user)
                    u.execute()
                    # create user score table for current room
                    userscore, score_is_created = UserRoomScore.get_or_create(
                        user_id=user,
                        gameroom_id=chat_id)
                    # add a point to winner's score
                    if userscore:
                        score = UserRoomScore.update(score=UserRoomScore.score + 1)\
                            .where(UserRoomScore.user_id == user, UserRoomScore.gameroom_id == chat_id)
                        score.execute()

                    ctx.bot.send_message(chat_id=upd.effective_chat.id, reply_to_message_id=upd.message.message_id,
                                         text='<b>Right answer from <i>%s</i></b> (scores: <b>%s</b>)! \n'
                                              'That really was: \n'
                                              '<pre>%s</pre> = <pre>%s</pre>' % (
                                                    upd.message.from_user.first_name, userscore.score + 1,
                                                    ctx.chat_data.get('active_game').get('riddle'),
                                                    ctx.chat_data.get('active_game').get('answer')),
                                         parse_mode=parsemode.ParseMode.HTML)
                    # start a new round if autostart was enabled
                    if ctx.chat_data.get('autostart'):
                        logger.warning('Ctx at autostart: %s' % str(ctx.chat_data))
                        timer = ctx.chat_data.get('settings').get('timer')
                        logger.warning('Timer at autostart: %s' % str(timer))
                        _start_new_round(upd, ctx, timer)
                    else:
                        # remove active game
                        ctx.chat_data['active_game'] = {}


def _start_new_round(upd, ctx, timer, dict_name=None):
    """Chooses new word from Game dictionary and starts new round. Runs a task to announce the right answer."""

    chat_id = upd.effective_chat.id

    if not dict_name:
        dict_name = GameRoom.get(tg_id=chat_id).dictionary_name
        if not dict_name:
            dict_name = DEFAULT_DICT_NAME

    filepath = os.path.join(DICTS_FOLDER, '%s.json' % dict_name)
    
    with open(filepath, 'r', encoding='utf-8') as fp:
        dictionary = json.load(fp)

    if 'settings' not in ctx.chat_data:
        ctx.chat_data['settings'] = {}
    if 'dict_name' not in ctx.chat_data['settings']:
        ctx.chat_data['settings']['dict_name'] = dict_name
    
    answer, riddle = choice(dictionary)

    logger.info("====="*5)
    logger.info("%s <--- %s" % (answer, riddle))
    logger.info("====="*5)

    if answer and riddle:  # riddle is found

        reply_text = '<i>%s</i>  is starting <b>a new game</b>!\n' \
                     'Guess the translation (<b>%s seconds left</b>): \n' \
                     '<pre>%s = %s</pre>' % (upd.message.from_user.first_name,
                                  timer,
                                  riddle, _mask_string(answer))

        game_room = GameRoom.get(tg_id=chat_id)
        autostart = game_room.autostart
        timer = game_room.timer

        ctx.chat_data['active_game'] = {}
        ctx.chat_data['active_game']['riddle'] = riddle
        ctx.chat_data['active_game']['answer'] = answer
        ctx.chat_data['active_game']['created_at'] = datetime.now()
        ctx.chat_data['settings']['timer'] = timer
        ctx.chat_data['active_game']['autostart'] = autostart

        ctx.job_queue.run_once(_send_answer_to_chat, timer,
                               context={'chat_id': chat_id,
                                        'answer': answer,
                                        'riddle': riddle,
                                        'autostart': autostart,
                                        'timer': timer,
                                        'original_update': upd,
                                        'original_context': ctx},
                               name=str(chat_id))

        # reply to user
        ctx.bot.send_message(chat_id=chat_id, reply_to_message_id=upd.message.message_id,
                             text=reply_text, parse_mode=parsemode.ParseMode.HTML)

    else:  # riddle or answer is not found
        logger.critical('Riddle is not found')


def start(upd, ctx):
    """
    Starts new game.
    Creates user for gamestarter and gameroom by their ownership.
    """
    logger.info('Starting new game: %s\n' % str(upd))

    # GROUP CHAT
    if upd.effective_chat.type == 'group':
        chat_id = upd.effective_chat.id

        # user started a game
        user_initiator, user_is_created = User.get_or_create(
            tg_id=upd.message.from_user.id,
            defaults={
                'username': upd.message.from_user.first_name
            })

        # create gameroom
        game_room, game_room_is_created = GameRoom.get_or_create(
            tg_id=chat_id,
            owner=user_initiator,
            defaults={
                'dictionary_name': DEFAULT_DICT_NAME,
                'timer': DEFAULT_TIMER,
                'autostart': False
            }
        )
        if game_room_is_created:
            logger.warning('New game room is created!\n')


        ctx.chat_data['autostart'] = game_room.autostart

        logger.warning('\nAutostart at start: %s \n' % ctx.chat_data['autostart'])

        if game_room:
            timer = game_room.timer
            autostart = game_room.autostart
            dict_name = game_room.dictionary_name

            # no active game
            if not ctx.chat_data.get('active_game') or \
                not 'timer' in ctx.chat_data.get('active_game') or \
                not 'riddle' in ctx.chat_data.get('active_game'):
                ctx.chat_data['settings'] = {}
                ctx.chat_data['settings']['timer'] = timer
                ctx.chat_data['active_game'] = {}
                ctx.chat_data['active_game']['autostart'] = autostart  # ?
                _start_new_round(upd, ctx, timer, dict_name)
            else:  # active game still not finished
                current_riddle = ctx.chat_data.get('active_game').get('riddle')
                current_answer = ctx.chat_data.get('active_game').get('answer')
                time_spent = (datetime.now() - ctx.chat_data.get('active_game').get('created_at')).seconds
                if time_spent < timer:
                    reply_text = 'Game is <b>still in progress</b>.\n' \
                                 'Time left: <b>%s sec</b>\n' \
                                 '<pre>%s = %s</pre>' % (timer - time_spent,
                                                         current_riddle, _mask_string(current_answer))

                    # reply to user
                    ctx.bot.send_message(chat_id=upd.effective_chat.id, reply_to_message_id=upd.message.message_id,
                                         text=reply_text, parse_mode=parsemode.ParseMode.HTML)
                # seems overhead
                # else:  # old game finished
                #     _start_new_round(upd, ctx, timer)
        else:  # no game room
            logger.warning('No game room')


    # PRIVATE CHAT
    elif upd.effective_chat.type == 'private':
        logger.warning(upd)
        reply_text = 'Hi! Add me to a group channel and send /start there.\n' \
                     'Привет! Добавь меня в групповой чат и напиши /start там.'
        ctx.bot.send_message(chat_id=upd.effective_chat.id, reply_to_message_id=upd.message.message_id,
                             text=reply_text)



def stop(upd, ctx):
    """
    Stops current game.
    Could be used when autostart enabled to finish generating new riddles till next manual game start.
    Removes all active jobs and ends a conversation.
    """

    chat_id = upd.effective_chat.id

    if not ctx.chat_data.get('active_game'):
        logger.warning('No active game!')
        return

    user = upd.message.from_user
    logger.warning('User %s canceled the conversation.' % user.first_name)

    reply_text = 'The game has stopped by  <i>%s</i>.\n' % user.first_name
    if ctx.chat_data.get('active_game'):
        reply_text += 'Last unguessed word was: \n' \
                      '<pre>%s</pre> = <pre>%s</pre>' % (ctx.chat_data.get('active_game').get('riddle'),
                                                         ctx.chat_data.get('active_game').get('answer'))

    upd.message.reply_text(text=reply_text, parse_mode=parsemode.ParseMode.HTML)

    ctx.chat_data['active_game'] = None
    current_jobs = ctx.job_queue.jobs()
    for job in current_jobs:
        # logger.warning(str(job))
        # logger.warning(str(job.context))
        if job.context['chat_id'] == chat_id:
            job.schedule_removal()

    return ConversationHandler.END


def display_info(upd, ctx):
    """Displays current Gameroom options."""
    chat_id = upd.effective_chat.id

    dict_name = None
    if not 'settings' in ctx.chat_data:
        ctx.chat_data['settings'] = {}
    if 'dict_name' in ctx.chat_data['settings']:
        dict_name = ctx.chat_data.get('settings').get('dict_name')

    if not ctx.chat_data.get('active_game'):
        user_initiator, user_is_created = User.get_or_create(
            tg_id=upd.message.from_user.id,
            defaults={
                'username': upd.message.from_user.first_name
            })

        # create gameroom
        game_room, game_room_is_created = GameRoom.get_or_create(
            tg_id=chat_id,
            owner=user_initiator,
            defaults={
                'dictionary_name': DEFAULT_DICT_NAME,
                'timer': DEFAULT_TIMER,
                'autostart': False}
        )
        room_timer = game_room.timer
        room_autostart = game_room.autostart
        if not dict_name:
            dict_name = game_room.dictionary_name
            ctx.chat_data['settings']['dict_name'] = dict_name

        logger.warning('\nCurrent game settings DB:\n\n'\
                 'Time for answer: %s seconds.\n'\
                 'Autostart enabled: %s.\n'\
                 'Dictionary name: %s' % (room_timer, room_autostart, dict_name))
    else:
        room_timer = ctx.chat_data.get('settings').get('timer', DEFAULT_TIMER)
        room_autostart = ctx.chat_data.get('active_game').get('autostart')
        if not dict_name:
            dict_name = ctx.chat_data.get('settings').get('dict_name')

        logger.warning('\nCurrent game settings ACTIVE GAME:\n\n'\
                 'Time for answer: %s seconds.\n'\
                 'Autostart enabled: %s.\n'\
                 'Dictionary name: %s' % (room_timer, room_autostart, dict_name))


    reply_text = '<b>Current game settings:</b>\n\n'\
                 'Time for answer: <b>%s seconds</b>.\n'\
                 'Autostart enabled: <b>%s</b>.\n'\
                 'Dictionary name: <b>%s</b>' % (room_timer, room_autostart, dict_name)

    ctx.bot.send_message(chat_id=upd.effective_chat.id, reply_to_message_id=upd.message.message_id,
                         text=reply_text, parse_mode=parsemode.ParseMode.HTML)


def display_top(upd, ctx):
    """Displays top TOP_USERS_AMOUNT_TO_DISPLAY leaderbord of current Gameroom."""
    chat_id = upd.effective_chat.id
    reply_text = ''

    room_users = User.select(User.username, UserRoomScore.score)\
        .join(UserRoomScore)\
        .where(UserRoomScore.gameroom_id == chat_id)\
        .order_by(UserRoomScore.score.desc()).dicts()

    for user in room_users[:TOP_USERS_AMOUNT_TO_DISPLAY]:
        reply_text += '%s: %s \n' % (user.get('username'), user.get('score'))
    ctx.bot.send_message(chat_id=upd.effective_chat.id, reply_to_message_id=upd.message.message_id,
                         text='<b>Top players in this room:</b>\n' + reply_text, parse_mode=parsemode.ParseMode.HTML)


def display_score(upd, ctx):
    """Displays user's total and Gameroom score."""
    user_id = upd.message.from_user.id
    chat_id = upd.effective_chat.id
    reply_text = ''

    user, user_is_created = User.get_or_create(
        tg_id=user_id,
        defaults={
            'username': upd.message.from_user.first_name
        })

    if user:
        total_score = user.score
        reply_text += 'Your total score: <b>%s</b>\n' % total_score
        userroomscore, roomscore_is_created = UserRoomScore.get_or_create(
            user_id=user,
            gameroom_id=chat_id)

        chat_score = userroomscore.score if userroomscore else 0
        reply_text = 'Your score in this room: <b>%s</b>' % chat_score + '\n' + reply_text

    ctx.bot.send_message(chat_id=chat_id,
                         reply_to_message_id=upd.message.message_id,
                         text=reply_text, parse_mode=parsemode.ParseMode.HTML)


def cancel(upd, ctx):
    user = upd.message.from_user
    logger.warning("User %s canceled the conversation.", user.first_name)
    upd.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END
