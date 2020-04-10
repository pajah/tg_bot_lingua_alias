from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from bot import bot
from handlers.commands import start, rock_paper_scissors
from handlers.messages import echo
from jobs.sample import broadcast_job

from markups.rock_paper_scissors import buttons

import logging


def bot_run():


    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    updater = Updater(bot=bot, workers=4, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(command='start', callback=start))
    # dp.add_handler(CommandHandler(command='rock', callback=rock_paper_scissors))
    dp.add_handler(MessageHandler(Filters.text(['/rock', '/stoprock'] + buttons), rock_paper_scissors))
    dp.add_handler(MessageHandler(Filters.text, echo))

    # updater.job_queue.run_repeating(broadcast_job, interval=60, first=0)

    updater.start_polling(clean=True)

    updater.idle()


if __name__ == '__main__':
    bot_run()
