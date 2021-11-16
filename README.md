# Advanced Project in Conversational Agents

Studying the effects of emojis and sentence sentiment on the user retention and user's feelings towards a chat-bot.
Experiment conducted as student project in the University of Twente 2020. 

# Requirements
This repository requires Python 3 in order to run.

Install dependencies by running:
```
pip3 install -r requirements.txt
```

### Secrets

Running the bot locally, does not require addition of any secrets.

In order to run the Telegram bot, you will need a [Big Huge Thesaurus API key](https://words.bighugelabs.com/site/api), and it needs to be included in the secrets.json file under `TheSaurusAPI`-key.
Furthermore one needs to [create a Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot), the bot token should then be included in the secrets.json file under `TelegramToken`-key.

### Other

For the Telegram bot to work properly, one needs to supply the code with a Trigram language model as `trigram_model.pickle` in the root directory. This is **not** supplied in the repository for the space limitations. Users of the repository will have to provide their own trigram model in the following format:

```
# Probability of word-pair "word_1 word_2" being followed by word_3
trigram_model = {(word_1, word_2): Probability(word_3)}
```

The trigram model used for the experiments has been lost, and cannot be provided anymore.

# Running the Telegram Bot

For the Telegram Bot to be able to respond to messages, the script `bot.py` needs to be actively running on a computer.

# Additional info

This repository facilitates an A/B test among the users. Part of the Telegram users will get a different responses from the bot.

Based on our findings, the addition of emojis and sentimental responses will have minor impact on the perception towards the chatbot. However, the retention should be expected to reduce significantly.