from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from api.telegram_bot import TOKEN

updater = Updater(token=TOKEN) # The Updater class continuously fetches new updates from telegram and passes them on to the Dispatcher class. If you create an Updater object, it will create a Dispatcher for you and link them together with a Queue. You can then register handlers of different types in the Dispatcher, which will sort the updates fetched by the Updater according to the handlers you registered, and deliver them to a callback function that you defined.

dispatcher = updater.dispatcher # For quicker access to the Dispatcher used by your Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # you will know when (and why) things don't work as expected
                    level=logging.INFO)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
