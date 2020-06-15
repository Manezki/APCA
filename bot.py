from programy.clients.embed.basic import EmbeddedDataFileBot
from sentiment import getSentiment, getEmoji
from mutate import mutateMessage, SynonymNotFound
import telegram
from telegram import update
from telegram.ext import (Updater, MessageHandler, Filters)
from telegram.error import NetworkError
import json
import logging
from os import path as op


SYNONYM_SWAP_ATTEMPT_LIMIT = 5


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


def answerTelegramMessage(messageUpdate, callbackContext):
    """
    Answers to messages posted on Telegram.
    """

    tg_logger.log(logging.INFO, "User {} send message: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), messageUpdate.message.text))

    bot = callbackContext.bot
    sender = messageUpdate.effective_user
    
    sender_id = int(sender["id"])
    message = messageUpdate.message.text

    bot_response = generateResponse(message, user_id=sender_id)

    bot.send_message(chat_id=messageUpdate.message.chat_id, text=bot_response)
    
    tg_logger.log(logging.INFO, "Bot responded to user {}: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), bot_response))

    j.run_once(survey_callback, 300, context=messageUpdate.message.chat_id)


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

    positive_user = user_sentiment > 0

    attempts = 1
    # If user's sentiment is negative, the bot's response should be more negative. And vice versa for the positive
    while ((positive_user and (bot_sentiment >= user_sentiment)) or ((not positive_user) and (bot_sentiment <= user_sentiment))):

        if attempts > SYNONYM_SWAP_ATTEMPT_LIMIT:
            break

        try:
            candidate_message = mutateMessage(bot_message)
            candidate_sentiment = getSentiment(candidate_message)

            if positive_user:
                if candidate_sentiment > bot_sentiment:
                    bot_sentiment = candidate_sentiment
                    bot_message = candidate_message
            else:
                if candidate_sentiment < bot_sentiment:
                    bot_sentiment = candidate_sentiment
                    bot_message = candidate_message

        except SynonymNotFound:
            # If swapping of the synonym is NOT possible, it should not be possible on the subsequent tries neither
            attempts += SYNONYM_SWAP_ATTEMPT_LIMIT
            break

        attempts += 1
    
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


def survey_callback(context: telegram.ext.CallbackContext):

    context.bot.send_message(chat_id=context.job.context, text='How are you finding our conversation so far? Please answer this short survey and let me know! \U0001F604 <a href="https://docs.google.com/forms/d/e/1FAIpQLSfDMBHoSnWCcHVQpw_LRCDt1vnfPIbboKliQX4gfIheSe4rFg/viewform?usp=sf_link"> Start Survey</a>',
parse_mode=telegram.ParseMode.HTML)
    tg_logger.log(logging.INFO, "Sent a survey link to chat {}".format(context.job.context))
    j.stop(context=context.job.context)


updater = Updater(token=tg_token, workers=1, use_context=True)
j = updater.job_queue
dispatcher = updater.dispatcher

dispatcher.add_handler(MessageHandler((~Filters.command) & Filters.text, answerTelegramMessage))
dispatcher.add_error_handler(errorLogger)

updater.start_polling()
