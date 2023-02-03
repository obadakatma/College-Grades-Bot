import os
import random

import pandas as pd
import telegram

TOKEN = os.environ['token']
bot = telegram.Bot(TOKEN)


def motivate():
    quote = pd.read_csv("quotes.csv", dtype={'likes': 'Int64', 'index': 'Int64'})
    while True:
        i = random.randint(0, 3001)
        if "inspirational" in quote["tags"][i]:
            motivationalMessage = "Quote of the day:\n" + quote["quote"][i]
            break
    dataframe = pd.read_csv("id.csv", dtype={'User_id': 'Int64', 'Chat_id': "Int64"})
    allIds = []
    for index in range(len(dataframe)):
        allIds.append(dataframe.loc[index, "Chat_id"])

    for Id in allIds:
        bot.send_message(chat_id=int(Id), text=motivationalMessage)


motivate()
