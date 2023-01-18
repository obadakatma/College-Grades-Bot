import os.path

import pandas as pd
import telegram
import yaml
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater


class Members():
    def __init__(self, TOKEN):
        self.updater = Updater(TOKEN, use_context=True)
        self.dataFrame = pd.read_csv("Members.csv", dtype={'User_id': 'Int64', 'Chat_id': 'Int64'})
        try:
            self.rowCounter = self.dataFrame["User_id"].values[-1] + 1
        except IndexError:
            self.rowCounter = 1
        self.name, self.ifname = range(2)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config = yaml.load(open(os.path.join(self.base_path, "Config.yaml")).read(), Loader=yaml.FullLoader)
        self.filtr = Filters.chat(chat_id=self.config["Chat_Id"]["id"])
        self.bot = telegram.Bot(TOKEN)
        self.startCommand = CommandHandler('start', self.start)
        self.conversation = ConversationHandler(
            entry_points=[CommandHandler('addname', self.setInfo, self.filtr)],
            states={
                self.name: [MessageHandler(self.filtr, self.setName)],
                self.ifname: [MessageHandler(self.filtr, self.checkName)]
            },
            fallbacks=[]
        )

    def storeInformation(self, update, context, row):
        if self.checkName(self.dataFrame, row, update, context):
            self.dataFrame.to_csv("Members.csv", index=False)
            return True
        else:
            return False

    def checkName(self, dataframe, row, update, context):
        if dataframe["Name"].isin([f"{update.message.text}".lower()]).any().any():
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="This name is already exist.\nEnter another name:")
            return False
        else:
            dataframe.loc[row, f"Name"] = f"{update.message.text}".lower()
            dataframe.loc[row, "Chat_id"] = update.message.chat_id
            dataframe.loc[row, "User_id"] = self.rowCounter
            return True

    def start(self, update, context):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="Welcome to My Marks Bot.\nTo use commands just press the Menu button.\nThis Bot made by @obadaalkatma")

    def setInfo(self, update, context):
        self.bot.send_message(chat_id=update.message.chat_id, text="Type your name")
        return self.name

    def setName(self, update, context):
        print("name :", update.message.text)
        if self.storeInformation(update, context, self.rowCounter):
            pass
        else:
            return self.name
        context.user_data["user Name"] = update.message.text
        self.bot.send_message(chat_id=update.message.chat_id,
                              text=f"Ok now we added your name  {update.message.text}  to the bot")
        self.rowCounter += 1
        return ConversationHandler.END
