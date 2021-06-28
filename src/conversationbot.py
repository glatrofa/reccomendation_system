"""
Forked from rogram modified from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py which is dedicated to the public domain under the CC0 license.

The bot is started and runs until we press Ctrl-C on the command line.

Usage:
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the bot.
"""

import logging, os
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

DATA_PATH = 'data/data_recorded.csv' # path for storing user data
SUGGESTION, EXPLANATION, COLLECTION = range(3) # states for main ConversationHandler
collected_data = {} # global dictionary for storing user data to file


def start(update: Update, _: CallbackContext) -> int:
    """Starts the conversation and asks the user about their favourite pizza."""
    reply_keyboard = [['Pizza 1', 'Pizza 2']]
    global collected_data
    collected_data = {}

    update.message.reply_text(
        'Hi! I\'m a test bot.\n'
        'Send /cancel to stop talking to me.\n'
        'Your chad id is: '+str(update.effective_chat.id)+'\n\n'
        'Please, choose a pizza from this list <link_here>:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return ASK

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func

from functools import wraps
@send_typing_action
def ask(update: Update, context: CallbackContext):
    """Print the lists movies link and take the user input."""
    # update.message.reply_text(
    #     'Please, choose a movie from this list <link_here>:'
    # )
    
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://image.tmdb.org/t/p/w400/8peYuPeLawgCFhuI4IcDjdrAAXw.jpg')


    return SUGGESTION


def pizza_suggestion(update: Update, _: CallbackContext):
    """Review the users' pizza and asks for a rating."""
    user = update.message.from_user
    logger.info("User name: %s, user choise: %s", user.first_name, update.message.text)
    global collected_data
    collected_data.update({'user': user.first_name})
    collected_data.update({'pizza_selected': update.message.text})
    update.message.reply_text(
        'This is my recomendation: bla bla\n\n'
        'Please, reate this recomendation within the 1-5 range:',
        reply_markup=ReplyKeyboardMarkup([['1', '2', '3', '4', '5']], one_time_keyboard=True),
    )
    
    return EXPLANATION


def user_explanation(update: Update, _: CallbackContext):
    """Gets the user rating and an explanation for it."""
    logger.info("User rating: %s", update.message.text)
    global collected_data
    collected_data.update({'rating': update.message.text})
    update.message.reply_text(
        'Got it, thanks for reviewing me.\n\n'
        'Please, explain your rating:',
    )
    
    return COLLECTION


def end_conversation(update: Update, _: CallbackContext):
    """Saves data to file and thanks the user."""
    logger.info("User rating explanation: %s, user chat id: %s", update.message.text, str(update.effective_chat.id))
    global collected_data
    collected_data.update({'rating_explanation': update.message.text})
    collected_data.update({'chad_id': update.effective_chat.id})
    update.message.reply_text(
        'Thank you!\n'
        'Your data is registered.',
        reply_markup=ReplyKeyboardRemove(),
    )

    save_to_file()

    return ConversationHandler.END


def save_to_file():
    """Saves values in collected_data in the DATA_PATH file."""
    global collected_data
    if not os.path.isfile(DATA_PATH):
        with open(DATA_PATH, 'w') as file:
            file.write('user;pizza_selected;rating;rating_explanation;chad_id;\n')
            logger.info('File created on '+DATA_PATH)
    
    try:
        with open(DATA_PATH, 'a') as file:
            file_entry = ''
            for s in collected_data.values():
                file_entry = file_entry+str(s)+';'
            file.write(file_entry+'\n')
    except Exception as e:
        logger.error('Unable to append on '+DATA_PATH+': '+str(e)+'.')


def cancel(update: Update, _: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        '✖ Conversation canceled.\n'
        'Please type /start to restart the conversation.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def echo(update: Update, _: CallbackContext):
    """Every words typed by the user outside the main conversation flow is tagged as not recognized."""
    update.message.reply_text(
        '⚠ Warning: message not recognized!\n'
        'To start the conversation, please type /start.',
    )

    return ConversationHandler.END


def unknown(update: Update, _: CallbackContext):
    """Notify to the user that the command typed does not exist."""
    update.message.reply_text(
        '😮 Sorry, this command does not exist.\n',
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states SUGGESTION, EXPLANATION and COLLECTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SUGGESTION: [MessageHandler(Filters.regex('^(Pizza 1|Pizza 2)$'), pizza_suggestion)],
            EXPLANATION: [MessageHandler(Filters.regex('^(1|2|3|4|5)$'), user_explanation)],
            COLLECTION: [MessageHandler(Filters.text & ~Filters.command, end_conversation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
