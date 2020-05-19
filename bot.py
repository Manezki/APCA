import aiml
from sentiment import getSentiment
from mutate import mutateMessage

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

    while (bot_sentiment <= user_sentiment) and (bot_sentiment < 0.75):
        bot_message = mutateMessage(bot_message)
        bot_sentiment = getSentiment(bot_message)
    
    print(bot_message)
