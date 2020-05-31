import random
from textblob import TextBlob

def getSentiment(text):
    analysis = TextBlob(text)
    user_sentiment_score = analysis.sentiment.polarity

    return user_sentiment_score


def getEmoji(text):
    love_list = ["\U0001f493", "\U0001f60d", "\U0001f618"]
    love_emoji = random.choice(love_list)
    surprised_list = ["\U0001f631", "\U0001f633", "\U0001f62e"]
    surprised_emoji = random.choice(surprised_list)
    awesome_list = ["\U0001f60e", "\U0001f60e"]
    awesome_emoji = random.choice(awesome_list)

    analysis = TextBlob(text)
    sentiment_score = analysis.sentiment.polarity

    if 0.3 > sentiment_score >= 0:
        return "\U0001f604"
    if 0.5 >= sentiment_score >= 0.3:
        return love_emoji
    elif 0.7 >= sentiment_score > 0.5:
        return surprised_emoji
    elif 0.8 >= sentiment_score > 0.7:
        return "\U0001f60a"
    elif 1 >= sentiment_score > 0.8:
        return awesome_emoji
    elif 0 > sentiment_score > -0.7:
        return "\U0001f625"
    elif -0.7 >= sentiment_score > -0.9:
        return "\U0001F912"
    elif -0.9 >= sentiment_score >= -1:
        return "\U0001F92E"
