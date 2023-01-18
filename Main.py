import os

import Members

TOKEN = os.environ['token']
members = Members.Members(TOKEN)
members.updater.dispatcher.add_handler(members.startCommand)

members.updater.dispatcher.add_handler(members.conversation)
members.updater.start_polling()
