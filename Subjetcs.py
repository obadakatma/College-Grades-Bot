import os
import re

from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.update import Update
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove
from telegram.ext.filters import Filters
from Init import Init
from mysql import connector
from createTable import PDF


class Subjects(Init):
    def __init__(self, TOKEN):
        super().__init__(TOKEN)
        self.message, self.markChanger = range(2)
        self.subjectNames = ["اضافة اسم مادة", "تعديل اسم مادة", "انتهيت"]
        self.subjectNamesButtons = [[KeyboardButton(name)] for name in self.subjectNames]
        self.setOrUpdateSubjectName = MessageHandler(
            Filters.regex(re.compile(r'\b(?:اضافة/تعديل اسم مادة)\b', re.IGNORECASE)) & self.filtr,
            self.changeOrAddName)
        self.response, self.newName = range(2)
        self.addSubjectNameMessage = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.regex(re.compile(r'\b(?:اضافة اسم مادة)\b', re.IGNORECASE)) & self.filtr & Filters.text,
                self.addSubject)],
            states={
                self.response: [MessageHandler(self.filtr & Filters.text, self.addSubjectName)]
            },
            fallbacks=[]
        )
        self.lastSubjectName = ""
        self.updateSubjectNameMessage = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.regex(re.compile(r'\b(?:تعديل اسم مادة)\b', re.IGNORECASE)) & self.filtr & Filters.text,
                self.updateSubject)],
            states={
                self.response: [MessageHandler(self.filtr & Filters.text, self.getLastSubjectName)],
                self.newName: [MessageHandler(self.filtr & Filters.text, self.updateSubjectName)]
            },
            fallbacks=[]
        )
        self.subName, self.year = range(2)
        self.SubjectName = ""
        self.setYearMessage = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.regex(re.compile(r'\b(?:اضافة/تعديل سنة المادة)\b', re.IGNORECASE)) & self.filtr & Filters.text,
                self.changeOrAddYear)],
            states={
                self.subName: [MessageHandler(self.filtr & Filters.text, self.getSubjectName)],
                self.year: [MessageHandler(self.filtr & Filters.text, self.getSubjectYear)]
            },
            fallbacks=[]
        )
        self.subMark = 2
        self.setYearMarkMessage = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.regex(re.compile(r'\b(?:اضافة/تعديل علامة عملي)\b', re.IGNORECASE)) & self.filtr & Filters.text,
                self.changeOrAddYearMark)],
            states={
                self.subName: [MessageHandler(self.filtr & Filters.text, self.getSubjectYearName)],
                self.subMark: [MessageHandler(self.filtr & Filters.text, self.updateYearMark)]
            },
            fallbacks=[]
        )
        self.setPaperMarkMessage = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.regex(re.compile(r'\b(?:اضافة/تعديل علامة نظري)\b', re.IGNORECASE)) & self.filtr & Filters.text,
                self.changeOrAddPaperMark)],
            states={
                self.subName: [MessageHandler(self.filtr & Filters.text, self.getSubjectPaperName)],
                self.subMark: [MessageHandler(self.filtr & Filters.text, self.updatePaperMark)]
            },
            fallbacks=[]
        )
        self.deleteSubject = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.regex(re.compile(r'\b(?:حذف مادة بكاملها)\b', re.IGNORECASE)) & self.filtr & Filters.text,
                self.deleteSub)],
            states={
                self.subName: [MessageHandler(self.filtr & Filters.text, self.getSubjectDeleteName)],
            },
            fallbacks=[]
        )
        self.doneMessage = MessageHandler(
            Filters.regex(re.compile(r'\b(?:انتهيت)\b', re.IGNORECASE)) & self.filtr & Filters.text,
            self.endMessage)
        self.getAllSubjectMarksMessage = MessageHandler(
            Filters.regex(re.compile(r'\b(?:عرض جميع العلامات)\b', re.IGNORECASE)) & self.filtr & Filters.text,
            self.marksPdf)

    def changeOrAddName(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="اختر الخيار الذي تريد إضافته",
                              reply_markup=ReplyKeyboardMarkup(self.subjectNamesButtons, resize_keyboard=True))

    def addSubject(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id, text="أدخل اسم المادة",
                              reply_markup=ReplyKeyboardRemove())
        return self.response

    def addSubjectName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if not res:
            cursor.execute(f'INSERT INTO Marks(chat_id,Subject) VALUES({update.message.chat_id},"{message}")')
            db.commit()

            self.bot.send_message(chat_id=update.message.chat_id, text="تم اضافة اسم المادة",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END
        else:
            self.bot.send_message(chat_id=update.message.chat_id, text="الاسم مخزن مسبقا",
                                  reply_markup=ReplyKeyboardMarkup(self.subjectNamesButtons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END

    def updateSubject(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id, text="أدخل اسم المادة القديمة",
                              reply_markup=ReplyKeyboardRemove())
        return self.response

    def getLastSubjectName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if res:
            self.lastSubjectName = message
            self.bot.send_message(chat_id=update.message.chat_id, text="قم بادخال اسم المادة الجديد")
            db.close()
            return self.newName
        else:
            self.bot.send_message(chat_id=update.message.chat_id, text="اسم المادة غير مخزن",
                                  reply_markup=ReplyKeyboardMarkup(self.subjectNamesButtons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END

    def updateSubjectName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if message == self.lastSubjectName:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="هذا الاسم هو نفسه اسم المادة القديم\nقم بادخال اسم جديد")
            db.close()
            return self.newName
        elif res:
            self.bot.send_message(chat_id=update.message.chat_id, text="اسم المادة مخزن مسبقا",
                                  reply_markup=ReplyKeyboardMarkup(self.subjectNamesButtons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END
        else:
            cursor = db.cursor()
            cursor.execute(
                f'UPDATE Marks SET Subject = "{message}" WHERE chat_id = {update.message.chat_id} AND Subject = "{self.lastSubjectName}"')
            db.commit()
            self.bot.send_message(chat_id=update.message.chat_id, text="تم تعديل اسم المادة",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            self.lastSubjectName = ""
            db.close()
            return ConversationHandler.END

    def changeOrAddYear(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id, text="أدخل اسم المادة",
                              reply_markup=ReplyKeyboardRemove())
        return self.subName

    def getSubjectName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if res:
            self.SubjectName = message
            self.bot.send_message(chat_id=update.message.chat_id, text="أدخل سنة المادة")
            db.close()
            return self.year
        else:
            self.bot.send_message(chat_id=update.message.chat_id, text="اسم المادة غير مخزن",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END

    def getSubjectYear(self, update: Update, context: CallbackContext):
        message = update.message.text
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        if message.isnumeric():
            cursor = db.cursor()
            cursor.execute(
                f'UPDATE Marks SET Year = "{message}" WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            db.commit()
            self.bot.send_message(chat_id=update.message.chat_id, text="تم اضافة/تعديل سنة المادة",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            self.SubjectName = ""
            db.close()
            return ConversationHandler.END
        else:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="يجب ان يكون سنة المادة كرقم\nقم بإدخال السنة مجددا")
            db.close()
            return self.year

    def changeOrAddYearMark(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id, text="أدخل اسم المادة",
                              reply_markup=ReplyKeyboardRemove())
        return self.subName

    def getSubjectYearName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if res:
            self.SubjectName = message
            self.bot.send_message(chat_id=update.message.chat_id, text="أدخل علامة العملي للمادة")
            db.close()
            return self.subMark
        else:
            self.bot.send_message(chat_id=update.message.chat_id, text="اسم المادة غير مخزن",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END

    def updateYearMark(self, update: Update, context: CallbackContext):
        message = update.message.text
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        if message.isnumeric():
            message = int(message)
            cursor = db.cursor()
            cursor.execute(
                f'UPDATE Marks SET YearMarks = "{message}" WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            db.commit()
            self.bot.send_message(chat_id=update.message.chat_id, text="تم اضافة/تعديل علامة العملي للمادة",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            cursor.execute(
                f'SELECT PaperMarks FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            res = cursor.fetchall()
            if res[0][0] is not None:
                cursor.execute(
                    f'UPDATE Marks SET FinalMark = "{res[0][0] + message}" WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            db.commit()
            self.SubjectName = ""
            db.close()
            return ConversationHandler.END
        else:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="يجب ان يكون علامة العملي المادة كرقم\nقم بإدخال علامة العملي مجددا")
            db.close()
            return self.subMark

    def changeOrAddPaperMark(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id, text="أدخل اسم المادة",
                              reply_markup=ReplyKeyboardRemove())
        return self.subName

    def getSubjectPaperName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if res:
            self.SubjectName = message
            self.bot.send_message(chat_id=update.message.chat_id, text="أدخل علامة النظري للمادة")
            db.close()
            return self.subMark
        else:
            self.bot.send_message(chat_id=update.message.chat_id, text="اسم المادة غير مخزن",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END

    def updatePaperMark(self, update: Update, context: CallbackContext):
        message = update.message.text
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        if message.isnumeric():
            message = int(message)
            cursor = db.cursor()
            cursor.execute(
                f'UPDATE Marks SET PaperMarks = "{message}" WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            db.commit()
            self.bot.send_message(chat_id=update.message.chat_id, text="تم اضافة/تعديل علامة النظري للمادة",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            cursor.execute(
                f'SELECT YearMarks FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            res = cursor.fetchall()
            if res[0][0] is not None:
                cursor.execute(
                    f'UPDATE Marks SET FinalMark = "{res[0][0] + message}" WHERE chat_id = {update.message.chat_id} AND Subject = "{self.SubjectName}"')
            db.commit()
            self.SubjectName = ""
            db.close()
            return ConversationHandler.END
        else:
            self.bot.send_message(chat_id=update.message.chat_id,
                                  text="يجب ان يكون علامة النظري المادة كرقم\nقم بإدخال علامة النظري مجددا")
            db.close()
            return self.subMark

    def deleteSub(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id, text="أدخل اسم المادة التي تريد حذفها",
                              reply_markup=ReplyKeyboardRemove())
        return self.subName

    def getSubjectDeleteName(self, update: Update, context: CallbackContext):
        message = update.message.text.lower()
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(f'SELECT Subject FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
        res = cursor.fetchall()
        if res:
            cursor.execute(
                f'DELETE FROM Marks WHERE chat_id = {update.message.chat_id} AND Subject = "{message}"')
            db.commit()
            self.bot.send_message(chat_id=update.message.chat_id, text="تم حذف المادة",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END
        else:
            self.bot.send_message(chat_id=update.message.chat_id, text="اسم المادة غير مخزن",
                                  reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))
            db.close()
            return ConversationHandler.END

    def endMessage(self, update: Update, context: CallbackContext):
        self.bot.send_message(chat_id=update.message.chat_id,
                              text="بإمكانك التحقق من العلامات من الزر عرض جميع العلامات"
                              , reply_markup=ReplyKeyboardMarkup(self.buttons, resize_keyboard=True))

    def marksPdf(self, update: Update, context: CallbackContext):
        db = connector.connect(
            host="localhost",
            user="root",
            password=f"{os.getenv('MYSQLPASS')}",
            database="Marks"
        )
        cursor = db.cursor()
        cursor.execute(
            f"SELECT Year,Subject,YearMarks,PaperMarks,FinalMark FROM Marks WHERE chat_id = '{update.message.chat_id}' ORDER BY Year,Subject")
        res = cursor.fetchall()
        data = [["Year", "Subject", "Paper mark", "Year mark", "Final mark"]]
        emdata = []
        for x in res:
            row = list(x)
            for i in range(len(x)):
                if row[3] is not None and row[4] is not None and row[4] < 60:
                    emdata.append(str(row[1]))
                row[i] = str(row[i])
            data.append(row)
        pdf = PDF()
        pdf.add_page()
        pdf.add_font("fo", '', fname="IBMPlexSansArabic-Regular.ttf")
        pdf.set_font("fo", '', size=12)
        pdf.create_table(table_data=data, title=f"{update.message.chat.full_name}'s Marks", x_start='C', align_data='C',
                         align_header='C', cell_width='30', emphasize_data=emdata, emphasize_style='',
                         emphasize_color=(255, 0, 0))
        pdf.ln()
        pdf.output('Marks.pdf')
        self.bot.send_document(chat_id=update.message.chat_id, document=open("Marks.pdf", 'rb'))
        db.close()
