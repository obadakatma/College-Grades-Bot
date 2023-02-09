import os

import Subjetcs

TOKEN = os.environ.get('TOKEN')
subjects = Subjetcs.Subjects(TOKEN)

subjects.updater.dispatcher.add_handler(subjects.startCommand)
subjects.updater.dispatcher.add_handler(subjects.registerCommand)
subjects.updater.dispatcher.add_handler(subjects.aboutCommand)
subjects.updater.dispatcher.add_handler(subjects.howToUseCommand)
subjects.updater.dispatcher.add_handler(subjects.setAllSubjectMarksConversation)
subjects.updater.dispatcher.add_handler(subjects.getAllSubjectMarksCommand)
subjects.updater.dispatcher.add_handler(subjects.changeYearMarkConversation)
subjects.updater.dispatcher.add_handler(subjects.changePaperMarkConversation)
subjects.updater.dispatcher.add_handler(subjects.sendMessageCommand)
subjects.updater.dispatcher.add_handler(subjects.receivedMessage)
subjects.updater.start_polling()
