# https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py

#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from api.telegram_bot import TOKEN

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

PIZZA, RECOMENDATION, EXPLANATION, RATING = range(4)


def start(update: Update, _: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['Pizza 1', 'Pizza 2']]

    update.message.reply_text(
        'Hi! I\'m a test bot.\n'
        'Send /cancel to stop talking to me.\n\n'
        'Please, choose a pizza from this list <link_here>:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return RECOMENDATION


def pizza_suggestion(update: Update, _: CallbackContext):
    user = update.message.from_user
    logger.info("User name: %s, user choise: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'This is my recomendation: bla bla\n\n'
        'Please, reate this recomendation:',
        reply_markup=ReplyKeyboardMarkup([['1', '2', '3', '4', '5']], one_time_keyboard=True),
    )
    
    return EXPLANATION


def user_explanation(update: Update, _: CallbackContext):
    logger.info("User rating: %s", update.message.text)
    update.message.reply_text(
        'Got it, thanks for reviewing me.\n\n'
        'Please, explain your rating:',
    )
    
    return RATING


def end_conversation(update: Update, _: CallbackContext):
    logger.info("User rating explanation: %s", update.message.text)
    update.message.reply_text(
        'Thank you!',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Conversation canceled.\n'
        'Please type /start to restart the conversation.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RECOMENDATION: [MessageHandler(Filters.regex('^(Pizza 1|Pizza 2)$'), pizza_suggestion)],
            EXPLANATION: [MessageHandler(Filters.regex('^(1|2|3|4|5)$'), user_explanation)],
            RATING: [MessageHandler(Filters.text & ~Filters.command, end_conversation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
