"""
Forked from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py which is dedicated to the public domain under the CC0 license.

The bot is started and runs until we press Ctrl-C on the command line.

Usage:
Send /start to initiate the conversation.
Send /cancel to end the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the bot.
"""

import logging, os, data_utils, telegram
import pandas as pd
from functools import wraps # to enable 'typing' label
from api.telegram import KEY as TELEGRAM_KEY
from api.tmdb import KEY as TMDB_KEY
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ChatAction
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from tmdbv3api import TMDb
from tmdbv3api import Movie

# enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# tmdb config
tmdb = TMDb()
tmdb.api_key = TMDB_KEY
tmdb.language = 'en'
# tmdb.debug = True
imdb_movie = Movie()

TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p/w200'
MOVIE_URL = 'https://www.themoviedb.org/movie/'
ASK, CHECK_MOVIE, SUGGESTION, EXPLANATION, COLLECTION = range(5) # states for main ConversationHandler

REVIEW_VALUES = ['1', '2', '3', '4', '5']

collected_data = {} # global dictionary for storing user data to file

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


@send_typing_action
def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and print a welcome message."""
    logger.info("%s - user %s initiated the chat", update.effective_chat.id, update.message.from_user.first_name)
    global collected_data
    collected_data = {}
    collected_data.update({'user': update.message.from_user.first_name})
    collected_data.update({'chat_id': update.effective_chat.id})

    update.message.reply_text(
        'Hi! I\'m a test bot.\n'
        'Send /cancel to stop talking to me.\n'
        'Your chat id is: '+str(update.effective_chat.id)
    )

    return ask(update, context)


@send_typing_action
def ask(update: Update, context: CallbackContext):
    """Send movies list link and take the user input."""
    update.message.reply_text(
        'Please, choose a movie from this list <link_here>:'
    )
    
    # context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://image.tmdb.org/t/p/w400/8peYuPeLawgCFhuI4IcDjdrAAXw.jpg')

    return CHECK_MOVIE








@send_typing_action
def check_movie(update: Update, context: CallbackContext):
    """Confirm to user his movie selected with a movie poster pic."""
    context.bot.sendMessage(chat_id=update.effective_chat.id, text='Select the movie:')
    movie = data_utils.get_movie_from_name(update.message.text)
    
    context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = 'You have selected ' + movie['title'].to_string(index=False) + ' (' + movie['year'].to_string(index=False) + ')' # there is a space before the year number
    )

    global imdb_movie
    tmdb_id = movie['tmdbId'].to_string(index=False)

    context.bot.send_photo(
        chat_id = update.effective_chat.id,
        photo = TMDB_IMAGE_URL +
                imdb_movie.details(tmdb_id).poster_path
    )

    global collected_data
    # collected_data.update({'movie_id': input_movie})
    movie_id = movie['movieId'].to_string(index=False)
    collected_data.update({'movie_id': movie_id}) # TODO: to convert in parameter function?
    collected_data.update({'movie_genres': movie['genres'].to_string(index=False).split('|')}) # get genres list
    logger.info("%s - user movie (id): %s", update.effective_chat.id, movie_id)

    return suggestion(update, context, movie_id)





@send_typing_action
def suggestion(update: Update, context: CallbackContext, movie_id):
    """Compute movie recommendation."""
    # TODO: save to file ids of movie recommended
    
    movie_list = data_utils.get_reccomended_movies(movie_id)
    context.bot.send_message(
        chat_id = update.effective_chat.id, 
        text = 'Here there is the reccomendation:'
    )

    genres_list = []

    for movie_id in movie_list:
        movie = data_utils.get_movie_from_id(int(movie_id))
        genres_list.append(movie[0][5]) # save genres for explanation
        print(movie)
        context.bot.send_photo(
            chat_id = update.effective_chat.id,
            photo = TMDB_IMAGE_URL +
                    imdb_movie.details(movie[0][4]).poster_path,
            caption = movie[0][1].capitalize() + '\n' + MOVIE_URL + str(movie[0][4])
        )

    return explanation(update, context, genres_list)


def explanation(update: Update, context: CallbackContext, genres_list: list):
    genre_list = []
    global collected_data
    collected_data['movie_genres']

    for element in genres_list:
        element = element.split('|')
        for genre in element:
            if (genre in collected_data['movie_genres']) and (genre not in genre_list):
                genre_list.append(genre)
    print(genre_list)

    update.message.reply_text(
        'These movies are reccomended because these genres are in common with your movie:\n' + ' '.join(genre_list)
    )

    return get_user_relevance(update, context)


def get_user_relevance(update: Update, context: CallbackContext):
    """Ask to the user his movie relevance."""

    question = (
        'Are these movies relevant for you?\n',
        'Please select a value from 1 to 5.'
    )

    update.message.reply_text(
        ''.join(question),
        reply_markup=ReplyKeyboardMarkup([REVIEW_VALUES], one_time_keyboard=True)
    )

    return COLLECTION
    # message = Bot.sendPoll(
    #     self = Bot,
    #     chat_id = update.effective_chat.id,
    #     question = 'bla bla',
    #     options = REVIEW_VALUES
    # )

#     button_list = [
#     InlineKeyboardButton("col1", callback_data=...),
#     InlineKeyboardButton("col2", callback_data=...),
#     InlineKeyboardButton("row 2", callback_data=...)
# ]
# reply_markup = InlineKeyboardMarkup(util.build_menu(button_list, n_cols=2))
# bot.send_message(..., "A two-column menu", reply_markup=reply_markup)



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
    # logger.info("User rating explanation: %s, user chat id: %s", update.message.text, str(update.effective_chat.id))
    # global collected_data
    # collected_data.update({'rating_explanation': update.message.text})
    # collected_data.update({'chad_id': update.effective_chat.id})
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
    if not os.path.isfile(data_utils.DATA_PATH):
        with open(data_utils.DATA_PATH, 'w') as file:
            file.write('user;pizza_selected;rating;rating_explanation;chad_id;\n')
            logger.info('File created on '+data_utils.DATA_PATH)
    
    try:
        with open(data_utils.DATA_PATH, 'a') as file:
            file_entry = ''
            for s in collected_data.values():
                file_entry = file_entry+str(s)+';'
            file.write(file_entry+'\n')
    except Exception as e:
        logger.error('Unable to append on '+data_utils.DATA_PATH+': '+str(e)+'.')


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
    # load movies datasets
    # global movies_data, movies_sim_data, movies_data_lower
    # movies_data = pd.read_csv(MOVIES_PATH)
    data_utils.load_data()

    updater = Updater(TELEGRAM_KEY) # create the Updater and pass it your bot's key.
    dispatcher = updater.dispatcher # get the dispatcher to register handlers

    # add conversation handler with the states SUGGESTION, EXPLANATION and COLLECTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK: [MessageHandler(Filters.text & ~Filters.command, ask)],
            CHECK_MOVIE: [MessageHandler(Filters.text & ~Filters.command, check_movie)],
            SUGGESTION: [MessageHandler(Filters.text & ~Filters.command, suggestion)],
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

    # start the Bot
    updater.start_polling()

    # run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
