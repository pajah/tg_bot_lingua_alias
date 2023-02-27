import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from markups.utils_menu import utils_menu

logger = logging.getLogger(__name__)

LITERS, MONEY, MILES = range(3)


def fuel_track(upd, ctx):
    msg = 'How many liters?'
    upd.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return LITERS


def liters(upd, ctx):
    text = upd.message.text
    ctx.user_data['liters'] = text
    msg = 'How many money for that?'
    upd.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return MONEY


def money(upd, ctx):
    text = upd.message.text
    ctx.user_data['money'] = text
    msg = 'How many miles?'
    upd.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return MILES


def miles(upd, ctx):
    # upd.message.reply_text('RASHOD:')
    text = upd.message.text
    ctx.user_data['miles'] = text
    # upd.message.reply_text('TUT CALCULATIONS', reply_markup=ReplyKeyboardRemove())

    try:
        mls = float(ctx.user_data['miles'])
        kms = mls * 1.60934
        grns = float(ctx.user_data['money'])
        ltrs = float(ctx.user_data['liters'])

        km_per_ltr = kms / ltrs
        ltr_per_1km = ltrs / kms
        avg_cons_per_100_km = ltr_per_1km * 100

    except ValueError:
        msg = 'You should pass only numbers with dot. Try again.'
        upd.message.reply_text(msg, reply_markup=utils_menu)
        return ConversationHandler.END

    except ZeroDivisionError:
        msg = 'Impossible to drive 0 miles or consume 0 fuel..'
        upd.message.reply_text(msg, reply_markup=utils_menu)
        return ConversationHandler.END


    msg = 'Calculated: \n' \
          '%s miles = %s km\n' \
          'Avg consuming: %s per 100 km\n' \
          'Km per 1 liter: %s\n' \
          'Each km costs %s hrn' % (str(mls)[:5], str(kms)[:5],
                                    str(avg_cons_per_100_km)[:5], str(km_per_ltr)[:5], str(grns / kms)[:5])

    logger.warning(str(ctx.user_data))
    upd.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(upd, ctx):
    user = upd.message.from_user
    logger.warning("User %s canceled the conversation.", user.first_name)
    upd.message.reply_text('Bye! I hope we can talk again some day.')

    return ConversationHandler.END



fuel_track_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('fuel_track', fuel_track)],

    states={
        LITERS: [MessageHandler(Filters.text, liters)],

        MONEY: [MessageHandler(Filters.text, money)],

        MILES: [MessageHandler(Filters.text, miles)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


