from programy.clients.embed.basic import EmbeddedDataFileBot
from sentiment import getSentiment, getEmoji
from mutate import mutateMessage, SynonymNotFound

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

my_bot = EmbeddedDataFileBot(files)

while True:
    user_message = input("Your message >>> ")
    user_sentiment = getSentiment(user_message)
    
    context = my_bot.create_client_context(0)
    bot_message = context.bot.ask_question(context, user_message)

    #bot_message = my_bot.ask_question(user_message)
    bot_sentiment = getSentiment(bot_message)
    # TODO This should be omitted after getSentiment works

    attempts = 0
    while (-1 <= user_sentiment <= 1) and (-1 <= bot_sentiment <= 1):
        attempts += 1
        try:
            bot_message = mutateMessage(bot_message)
            bot_emoji = getEmoji(user_message)
            # TODO This should be omitted after getSentiment works

            if attempts > 5:
                break

        except SynonymNotFound:
            break

    print(bot_message + bot_emoji)
