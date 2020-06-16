from programy.clients.embed.basic import EmbeddedDataFileBot
from sentiment import getSentiment, getEmoji
from mutate import mutateMessage, SynonymNotFound
from filters import private
import telegram
from telegram import update
from telegram import update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler)
from telegram.error import NetworkError
import json
import logging
from os import path as op
import os


SYNONYM_SWAP_ATTEMPT_LIMIT = 5
USER_HISTORY_DIRECTORY = op.join(op.dirname(__file__), "user_histories")

if not op.exists(USER_HISTORY_DIRECTORY):
    os.makedirs(USER_HISTORY_DIRECTORY)

chatbot_files = {'aiml': ['rosie-master/lib/aiml'],
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


def start(update, context):

    # Skip if user has already given consent
    if int(update.effective_user.id) in ___consents:
        return

    keyboard = [[InlineKeyboardButton("Yes", callback_data='1')],
                [InlineKeyboardButton("No", callback_data='2')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please provide your consent for using your information for '
                              'our research. By clicking "Yes", you allow us to use your '
                              'User ID, chat data and your survey results. You can then proceed to start a '
                              'conversation with the bot. If you click "No", your data will '
                              'be discarded by us and will not be used in our research', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query

    query.answer()

    if query.data == "1":
        query.edit_message_text(text="Thank you for participating in our research. You can now start a "
                                     "conversation with the bot.")
        tg_logger.log(logging.INFO, "User {} gave a consent".format(update.effective_user.id))

        # Skip if user has already given consent
        if int(update.effective_user.id) in ___consents:
            return

        ___consents.add(int(update.effective_user.id))

        # Assign different callbacks to users in groups A and B
        if (int(update.effective_user.id) % 2) == 0:
            context.job_queue.run_once(surveyCallbackControlGroup, 180, context=update.callback_query.message.chat.id)
        else:
            context.job_queue.run_once(surveyCallbackExperimentGroup, 180, context=update.callback_query.message.chat.id)

        # Re-engage in conversation after 23 hours
        context.job_queue.run_once(reengageConversation, 82800, context=update.callback_query.message.chat.id)
        
    elif query.data == "2":
        query.edit_message_text(
            text="Thank you for your time. Your data will not be used in our research. You can still "
                 "converse with the bot, but your data won't be recorded.")
        tg_logger.log(logging.INFO, "User {} user did not give a consent".format(update.effective_user.id))


def answerTelegramMessage(messageUpdate, callbackContext):
    """
    Answers to messages posted on Telegram.
    """

    tg_logger.log(logging.INFO, "User {} send message: {}".format((messageUpdate.effective_user.id, messageUpdate.effective_user.username), messageUpdate.message.text))

    bot = callbackContext.bot
    sender = messageUpdate.effective_user
    
    sender_id = int(sender["id"])
    message = messageUpdate.message.text


    # TODO Users should be added to the consents-set when they give consent
    if sender_id in ___consents:
        with open(op.join(USER_HISTORY_DIRECTORY, str(sender_id) + ".txt"), "a") as history:
            line = message.replace("\n", " ")
            history.write(line + "\n")


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


def surveyCallbackControlGroup(context: telegram.ext.CallbackContext):

    context.bot.send_message(chat_id=context.job.context, text='How are you finding our conversation so far? Please answer this short survey and let me know! \U0001F604 <a href="https://docs.google.com/forms/d/e/1FAIpQLScUQZTSbJEAHzHQ7-2-S7w1N4k8Eo3kXSmFbKyc8-7EEo72Fw/viewform?usp=sf_link"> Start Survey</a>',
parse_mode=telegram.ParseMode.HTML)
    tg_logger.log(logging.INFO, "Sent a survey link to chat {}".format(context.job.context))


def surveyCallbackExperimentGroup(context: telegram.ext.CallbackContext):

    context.bot.send_message(chat_id=context.job.context, text='How are you finding our conversation so far? Please answer this short survey and let me know! \U0001F604 <a href="https://docs.google.com/forms/d/e/1FAIpQLSfDMBHoSnWCcHVQpw_LRCDt1vnfPIbboKliQX4gfIheSe4rFg/viewform?usp=sf_link"> Start Survey</a>',
parse_mode=telegram.ParseMode.HTML)
    tg_logger.log(logging.INFO, "Sent a survey link to chat {}".format(context.job.context))


def reengageConversation(context: telegram.ext.CallbackContext):

    context.bot.send_message(chat_id=context.job.context, text='Hey, how are you doing today?',
parse_mode=telegram.ParseMode.HTML)
    tg_logger.log(logging.INFO, "Re-engaged in a conversation in chat: {}".format(context.job.context))


___consents = set()
chatbot = EmbeddedDataFileBot(chatbot_files)

updater = Updater(token=tg_token, workers=1, use_context=True)
j = updater.job_queue
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start, filters=private))
dispatcher.add_handler(CallbackQueryHandler(button, pass_job_queue=True))

dispatcher.add_handler(MessageHandler((~Filters.command) & Filters.text & private, answerTelegramMessage))
dispatcher.add_error_handler(errorLogger)

updater.start_polling()
print("Ready to receive messages")
