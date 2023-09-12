import os

from Subjetcs import Subjects

TOKEN = os.getenv("TOKEN")
subjects = Subjects(TOKEN)

dp = subjects.updater.dispatcher
dp.add_handler(subjects.startCommand)
dp.add_handler(subjects.registerCommand)
dp.add_handler(subjects.aboutMessage)
dp .add_handler(subjects.allCommand)
dp.add_handler(subjects.setOrUpdateSubjectName)
dp.add_handler(subjects.addSubjectNameMessage)
dp.add_handler(subjects.updateSubjectNameMessage)
dp.add_handler(subjects.setYearMessage)
dp.add_handler(subjects.setYearMarkMessage)
dp.add_handler(subjects.setPaperMarkMessage)
dp.add_handler(subjects.deleteSubject)
dp.add_handler(subjects.doneMessage)
dp.add_handler(subjects.getAllSubjectMarksMessage)
dp.add_handler(subjects.replyMessage)
dp.add_handler(subjects.receivedSticker)


subjects.updater.start_polling()
subjects.updater.idle()
