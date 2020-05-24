import aiml
from sentiment import getSentiment
from mutate import mutateMessage, SynonymNotFound

# Create the kernel and learn AIML files
kernel = aiml.Kernel()
kernel.learn("AIMLs/*.aiml")

# Press CTRL-C to break this loop
while True:

    # Framework for the bot
    user_message = input(">>>")
    user_sentiment = getSentiment(user_message)

    bot_message = kernel.respond(user_message)
    bot_sentiment = getSentiment(bot_message)
    bot_sentiment = 0.5

    while (bot_sentiment <= user_sentiment) and (bot_sentiment < 0.75):
        try:
            bot_message = mutateMessage(bot_message)
            bot_sentiment = getSentiment(bot_message)
            bot_sentiment = 1.0
        except SynonymNotFound:
            break
    
    print(bot_message)
