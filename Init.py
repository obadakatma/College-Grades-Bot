import pandas as pd
import telegram
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.updater import Updater


class Init:
    def __init__(self, TOKEN):

        self.updater = Updater(TOKEN, use_context=True)
        self.idCsv = pd.read_csv("id.csv", dtype={'Chat_id': 'Int64', 'User_id': 'Int64'})
        try:
            self.row = self.idCsv["User_id"].values[-1] + 1
        except IndexError:
            self.row = 1
        self.config = []
        for i in range(len(self.idCsv)):
            self.config.append(self.idCsv.loc[i, "Chat_id"])
        self.filtr = Filters.chat(self.config)
        self.bot = telegram.Bot(TOKEN)
        self.startCommand = CommandHandler('start', self.start)
        self.registerCommand = CommandHandler('register', self.register)
        self.howToUseCommand = CommandHandler('how_to_use', self.howToUse, self.filtr)
        self.aboutCommand = CommandHandler('about', self.about)

    def start(self, update, context):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="Welcome to My Marks Bot.\nTo use commands just press the Menu button.\nThis Bot made by @obadaalkatma\nأهلا وسهلا في بوت MyMarks\nلمعرفة الاوامر المتاحة انقر عل زر menu")

    def about(self, update, context):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="This bot just for storing the marks during the college years\nهذا البوت لتخزين العلامات خلال سنوات الجامعة")

    def register(self, update, context):
        if self.idCsv['Chat_id'].isin([int(update.message.chat_id)]).any().any():
            self.bot.send_message(chat_id=update.message.chat_id, text="You are registered already\nأنت مسجل مسبقا")
        else:
            self.idCsv.loc[self.row, "Chat_id"] = int(update.message.chat_id)
            self.idCsv.loc[self.row, "User_id"] = int(self.row)
            self.row += 1
            self.idCsv.to_csv("id.csv", index=False)
            self.filtr.add_chat_ids(update.message.chat_id)
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="Now you can use the bot\nالان أصبح بإمكانك استخدم البوت")

    def howToUse(self, update, context):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="To learn how to use the bot click the link below⬇️\nلمعرفة كيفية استخدام البوت انقر على الرابط في الأسفل⬇️")
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="https://drive.google.com/file/d/1Uh2-za6mOev2vE6T-j4kY7Q4ikl3z3FH/view?usp=share_link")
