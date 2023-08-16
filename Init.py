import re
import telegram
from telegram.ext.filters import Filters
from telegram.ext.updater import Updater
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update
import logging


class Init:
    def __init__(self, TOKEN):
        self.updater = Updater(TOKEN, use_context=True)
        self.bot = telegram.Bot(TOKEN)
        self.config = []
        with open('id.txt', 'r') as file:
            for id in file:
                self.config.append(int(id[:-1]))
        self.filtr = Filters.chat(self.config)
        self.buttonsName = ["اضافة/تعديل اسم مادة", "اضافة/تعديل سنة المادة", "اضافة/تعديل علامة عملي",
                            "اضافة/تعديل علامة نظري",
                            "عرض جميع العلامات", "حذف مادة بكاملها ⚠️️", "حول البوت ️ℹ️"]
        self.buttons = [[KeyboardButton(name)] for name in self.buttonsName]
        self.startCommand = CommandHandler('start', self.start)
        self.registerCommand = CommandHandler('register', self.register)
        self.aboutMessage = MessageHandler(Filters.regex(re.compile(r'\b(?:حول البوت)\b', re.IGNORECASE)) & self.filtr,
                                           self.about)
        self.sendMessageCommand = CommandHandler("sendMessage", self.sendMessage)
        self.receivedMessage = MessageHandler(filters=Filters.text, callback=self.receiveMessage)
        self.receivedSticker = MessageHandler(filters=Filters.sticker, callback=self.receiveSticker)

    def start(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text=f"اهلا {update.message.chat.full_name}\nهذا البوت سيساعدك على تخزين علامتك\nمطور البوت @obadaalkatma",
                              reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))

    def about(self, update, context):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="هذا البوت لتخزين العلامات خلال سنوات الجامعة\nإذا واجهت صعوبة في استخدام البوت فقط أرسل مشكلتك برسالة ضمن هذا البوت و بأسرع وقت سنرد عليك",
                              reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))

    def register(self, update, context):
        found = False
        userid = update.message.chat_id
        with open("id.txt", "r") as Id:
            if str(userid) in Id.read():
                found = True
            Id.close()
        with open("id.txt", "a") as Id:
            if not found:
                Id.write(f"{userid}\n")
            Id.close()
        if found:
            self.bot.send_message(chat_id=update.message.chat_id, text="أنت مسجل مسبقا",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
        else:
            self.filtr.add_chat_ids(update.message.chat_id)
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="الان أصبح بإمكانك استخدم البوت",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))

    def error(update, context):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.warning('Update "%s" caused error "%s"', update, context.error)


    def receiveMessage(self, update, context):
        self.bot.send_message(chat_id=853193305,
                              text=f"Username : {update.message.chat.username} | Name : {update.message.chat.full_name}\nMessage: {update.message.text}")

        self.bot.send_message(chat_id=853193305, text=f"Chat_Id : {update.message.chat_id}")

    def receiveSticker(self, update, context):
        self.bot.send_message(chat_id=853193305,
                              text=f"Username : {update.message.chat.username} | Name : {update.message.chat.full_name}")
        self.bot.sendSticker(chat_id=853193305, sticker=update.message.sticker)
        self.bot.send_message(chat_id=853193305, text=f"Chat_Id : {update.message.chat_id}")

    def sendMessage(self, update, context):
        message = f"{update.message.text}"
        chatId = int(message.split(" ")[1])
        message = message.split(' ')[2:]
        text = ""
        for index in message:
            text += index + ' '
        self.bot.send_message(chat_id=chatId, text=text)
