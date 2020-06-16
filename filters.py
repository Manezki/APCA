from telegram.ext import BaseFilter

class PrivateChat(BaseFilter):
    def filter(self, message):
        return message.chat.type == "private"

# Need to initialize the class in order to use.
private = PrivateChat()
