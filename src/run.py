from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler

from bot import bot
from handlers.commands import start, stop, check_user_message_for_answer, check_for_bot_abuse, display_help, \
    display_top, display_score, display_info, cancel

from handlers.change_dict import display_dict_list, dict_set
from handlers.admin_settings import set_admin_settings, set_autostart, set_timer
# from jobs.sample import broadcast_job


import logging


def debug(upd, ctx):
    # msg = '%s' % str(dir(ctx))
    # msg = '%s' % str(ctx.bot.get_chat(-438360875).get_members_count())

    msg = '%s' % str(upd) + str(ctx.chat_data)
    ctx.bot.send_message(upd.effective_chat.id, msg)


def bot_run():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    updater = Updater(bot=bot, workers=4, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler(command='start', callback=start))
    dp.add_handler(CommandHandler(command='stop', callback=stop))
    dp.add_handler(CommandHandler(command='info', callback=display_info))
    dp.add_handler(CommandHandler(command='help', callback=display_help))
    dp.add_handler(CommandHandler(command='top', callback=display_top))
    dp.add_handler(CommandHandler(command='score', callback=display_score))

    dp.add_handler(CommandHandler('settings', set_admin_settings))
    dp.add_handler(CommandHandler(command='set_timer', callback=set_timer))
    dp.add_handler(CommandHandler(command='set_autostart', callback=set_autostart))

    dp.add_handler(CommandHandler(command='debug', callback=debug))

    DICT_LIST, DICT_SET, DICT_DONE = map(chr, range(3))
    change_dict_handler = ConversationHandler(
        entry_points=[CommandHandler('set_dict', display_dict_list)],

        states={
        DICT_SET: [MessageHandler(Filters.text, dict_set)],
        # FUEL_LIST: [MessageHandler(Filters.text, fuel_list)],
        # FUEL_LITERS: [MessageHandler(Filters.text, fuel_liters)],
        # FUEL_MONEY: [MessageHandler(Filters.text, fuel_money)],
        # FUEL_MILES: [MessageHandler(Filters.text, fuel_miles)],
        # FUEL_SAVE: [MessageHandler(Filters.text, fuel_save)]
    },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(change_dict_handler)

    # dp.add_handler(MessageHandler(Filters.text, callback=check_for_bot_abuse))
    dp.add_handler(MessageHandler(Filters.text, callback=check_user_message_for_answer), group=1)





    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    bot_run()

