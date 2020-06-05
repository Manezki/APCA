from programy.clients.embed.basic import EmbeddedDataFileBot
from sentiment import getSentiment, getEmoji
from mutate import mutateMessage, SynonymNotFound
import telegram
from telegram.ext import (Updater, MessageHandler, Filters)
from telegram.error import NetworkError
import json
import logging
from os import path as op


files = {'aiml': ['rosie-master/lib/aiml'],
         'properties': 'rosie-master/lib/system/rosie.properties',
         'defaults': 'rosie-master/lib/system/rosie.pdefaults',
         'sets': ['rosie-master/lib/sets'],
         'maps': ['rosie-master/lib/maps'],
         'denormals': 'rosie-master/lib/substitutions/denormal.substitution',
         'normals': 'rosie-master/lib/substitutions/normal.substitution',
         'genders': 'rosie-master/lib/substitutions/gender.substitution',
         'persons': 'rosie-master/lib/substitutions/person.substitution',
         'person2s': 'rosie-master/lib/substitutions/person2.substitution',
         }

chatbot = EmbeddedDataFileBot(files)

# Logger configuration needs to be AFTER EmbeddedDataFileBot invokation
tg_logger = logging.getLogger('APCA')
tg_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(filename=op.join(op.dirname(__file__), "log.txt"), mode="a")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)

tg_logger.addHandler(fh)


with open("secrets.json", "r") as secrets:
    tg_token = json.load(secrets)["TelegramToken"]


def asnwerTelegramMessage(messageUpdate, callbackContext):
    """
    Answers to messages posted on Telegram.
    """

    tg_logger.log(logging.INFO, "User {} send message: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), messageUpdate.message.text))

    bot = callbackContext.bot
    sender = messageUpdate.effective_user
    
    sender_id= int(sender["id"])
    message = messageUpdate.message.text

    bot_response = generateResponse(message, user_id=sender_id)

    bot.send_message(chat_id=messageUpdate.message.chat_id, text=bot_response)
    
    tg_logger.log(logging.INFO, "Bot responded to user {}: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), bot_response))


def generateControlGroupResponse(user_message, user_id=0):
    """
    Given message from user, generates an answer to the user.
    """
    context = chatbot.create_client_context(user_id)

    bot_message = context.bot.ask_question(context, user_message)

    return bot_message


def generateExperimentGroupResponse(user_message, user_id=0):
    """
    Given message from user, generates an answer to the user.
    """
    user_sentiment = getSentiment(user_message)

    context = chatbot.create_client_context(user_id)    
    
    bot_message = context.bot.ask_question(context, user_message)
    bot_sentiment = getSentiment(bot_message)

    attempts = 0
    # BUG Does not iterate till sentiment is amplified
    while (-1 <= user_sentiment <= 1) and (-1 <= bot_sentiment <= 1):
        attempts += 1
        try:
            bot_message = mutateMessage(bot_message)
            # BUG Does not check if bot sentiment is higher than the user message

            if attempts > 5:
                break

        except SynonymNotFound:
            break
    
    bot_emoji = getEmoji(bot_message)

    return bot_message + bot_emoji


def generateResponse(user_message, user_id=0):
    """
    Assigns the user into an A/B test-group, and returns a response for the user.
    """
    # Split users based on their user-id. Should be 50/50 split
    if (user_id % 2) == 0:
        return generateControlGroupResponse(user_message, user_id)
    else:
        return generateExperimentGroupResponse(user_message, user_id)


def errorLogger(update, context):

    # Pass network errors, as they can flood the log-file
    if isinstance(update, NetworkError):
        pass
    else:
        tg_logger.log(logging.ERROR, "TelegramError: {} raised when processing following update: {}".format(context.error,
                                                                                                         update))


updater = Updater(token=tg_token, workers=1, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(MessageHandler((~Filters.command) & Filters.text, asnwerTelegramMessage))
dispatcher.add_error_handler(errorLogger)

updater.start_polling()
