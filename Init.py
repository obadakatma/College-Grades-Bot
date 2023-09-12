import logging
import os
import re

import telegram
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.update import Update


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
        self.allCommand = CommandHandler('all',self.all)
        self.aboutMessage = MessageHandler(Filters.regex(re.compile(r'\b(?:حول البوت)\b', re.IGNORECASE)) & self.filtr,
                                           self.about)
        self.receivedSticker = MessageHandler(filters=Filters.sticker, callback=self.receiveSticker)
        self.replyMessage = MessageHandler(filters=Filters.text, callback=self.handle_reply)

    def start(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text=f"اهلا {update.message.chat.full_name}\nهذا البوت سيساعدك على تخزين علامتك\nمطور البوت @obadaalkatma",
                              reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))

    def about(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="هذا البوت لتخزين العلامات خلال سنوات الجامعة\nإذا واجهت صعوبة في استخدام البوت فقط أرسل مشكلتك برسالة ضمن هذا البوت و بأسرع وقت سنرد عليك",
                              reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))

    def register(self, update: Update, context: CallbackContext):
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

    def error(update: Update, context: CallbackContext):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def receiveMessage(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=int(os.getenv("CHATID")),
                              text=f"Username : {update.message.chat.username} | Name : {update.message.chat.full_name}\nMessage: {update.message.text}")
        self.bot.send_message(chat_id=int(os.getenv("CHATID")), text=f"Chat_Id : {update.message.chat_id}")

    def receiveSticker(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=int(os.getenv("CHATID")),
                              text=f"Username : {update.message.chat.username} | Name : {update.message.chat.full_name}")
        self.bot.sendSticker(chat_id=int(os.getenv("CHATID")), sticker=update.message.sticker)
        self.bot.send_message(chat_id=int(os.getenv("CHATID")), text=f"Chat_Id : {update.message.chat_id}")

    def is_reply_to_bot(self, update: Update) -> bool:
        return (
                update.message.reply_to_message is not None
                and update.message.reply_to_message.from_user.id == self.bot.id
        )

    def handle_reply(self, update: Update, context) -> None:
        if self.is_reply_to_bot(update) and update.message.chat_id == int(os.getenv("CHATID")):
            messaeg = update.message.text
            replyToMessage = update.message.reply_to_message.text
            try:
                chatId = int(replyToMessage[replyToMessage.rfind(" "):])
                self.bot.send_message(chat_id=chatId, text=messaeg)
            except:
                self.bot.send_message(chat_id=update.message.chat_id, text="Wrong message")

        else:
            self.receiveMessage(update, context)

    def all(self, update: Update, context: CallbackContext):
        message = update.message.text[5:]
        if message == "" and update.message.chat_id == int(os.getenv("CHATID")):
            self.bot.send_message(chat_id=int(os.getenv("CHATID")), text="The message is empty.\nPlease resend it.")
        elif update.message.chat_id != int(os.getenv("CHATID")):
            self.bot.send_message(chat_id=update.message.chat_id, text="Only bot admins can use this command")
        else:
            if update.message.chat_id == int(os.getenv("CHATID")):
                with open("id.txt", "r") as file:
                    for id in file:
                        try:
                            self.bot.send_message(chat_id=int(id[:-1]), text=message)
                        except Exception as e:
                            print(e)
