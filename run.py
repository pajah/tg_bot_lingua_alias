from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from bot import bot
from handlers.commands import start, utils
from handlers.fuel_track import fuel_track_conv_handler
# from handlers.messages import echo
from jobs.sample import broadcast_job

# from markups.rock_paper_scissors import buttons

import logging


def bot_run():

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=20)

    logger = logging.getLogger(__name__)

    updater = Updater(bot=bot, workers=4, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(command='start', callback=start))
    dp.add_handler(CommandHandler(command='utils', callback=utils))

    dp.add_handler(fuel_track_conv_handler)

    # updater.job_queue.run_repeating(broadcast_job, interval=60, first=0)

    updater.start_polling(clean=True)
    logger.info('Polling started.')

    updater.idle()


if __name__ == '__main__':
    bot_run()
