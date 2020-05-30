import aiml
from sentiment import getSentiment
from mutate import mutateMessage, SynonymNotFound
import telegram
from telegram.ext import (Updater, MessageHandler, Filters)
from telegram.error import NetworkError
import json
import logging
from os import path as op

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                     level=logging.INFO,
                     datefmt='%m-%d %H:%M:%S',
                     filename=op.join(op.dirname(__file__), "log.txt"),
                     filemode="a")

# Create the kernel and learn AIML files
kernel = aiml.Kernel()
kernel.learn("AIMLs/*.aiml")

with open("secrets.json", "r") as secrets:
    tg_token = json.load(secrets)["TelegramToken"]


def asnwerTelegramMessage(messageUpdate, callbackContext):

    logging.log(logging.INFO, "User {} send message: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), messageUpdate.message.text))

    bot = callbackContext.bot
    sender = messageUpdate.effective_user
    
    sender_id= int(sender["id"])
    message = messageUpdate.message.text

    bot_response = generateResponse(message, user_id=sender_id)

    bot.send_message(chat_id=messageUpdate.message.chat_id, text=bot_response)
    logging.log(logging.INFO, "Bot responded to user {}: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), bot_response))
    return


def generateResponse(user_message, user_id=0):
    user_sentiment = getSentiment(user_message)

    bot_message = kernel.respond(user_message, sessionID=user_id)
    bot_sentiment = getSentiment(bot_message)
    # TODO This should be omitted after getSentiment works
    bot_sentiment = 0.5

    attempts = 0
    while (bot_sentiment <= user_sentiment) and (bot_sentiment < 0.75):
        attempts += 1
        try:
            bot_message = mutateMessage(bot_message)
            bot_sentiment = getSentiment(bot_message)
            # TODO This should be omitted after getSentiment works
            bot_sentiment = 1.0

            if attempts > 5:
                break

        except SynonymNotFound:
            break
    
    return bot_message


def errorLogger(update, context):

    if isinstance(update, NetworkError):
        pass
    else:
        logging.log(logging.ERROR, "TelegramError: {} raised when processing following update: {}".format(context.error,
                                                                                                         update))


updater = Updater(token=tg_token, workers=1, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(MessageHandler((~Filters.command) & Filters.text, asnwerTelegramMessage))
dispatcher.add_error_handler(errorLogger)

updater.start_polling()
