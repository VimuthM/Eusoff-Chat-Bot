from .models import chatb_collection, chatb_history

import requests
import os
import datetime
import pytz

TELEGRAM_URL = "https://api.telegram.org/bot"
TUTORIAL_BOT_TOKEN = os.getenv("TUTORIAL_BOT_TOKEN", "error_token")

count = 0
waitMessage = "Looking for another match."
messageDict = {}

# chatbot = ChatBot(
#         'Herbert',
#         logic_adapters=[
#             'chatterbot.logic.BestMatch',
#             'chatterbot.logic.MathematicalEvaluation'
#         ]
#     )

# @background(schedule=0)


def match(t_id):
    # inQueue = chatb_collection.count_documents({"state": "queued"})
    # personsInQueue = chatb_collection.find({"state": "queued"})

    # for i in range(0, inQueue - 1, 2):
    #     person1 = personsInQueue[i]["chat_id"]
    #     person2 = personsInQueue[i + 1]["chat_id"]

    #     chatb_collection.update_one(
    #         queryChatId(person1),
    #         {"$set": {"match_id": person2}}
    #     )
    #     chatb_collection.update_one(
    #         queryChatId(person2),
    #         {"$set": {"match_id": person1}}
    #     )
    #     chatb_collection.update_one(
    #         queryChatId(person1),
    #         {"$set": {"state": "matched"}}
    #     )
    #     chatb_collection.update_one(
    #         queryChatId(person2),
    #         {"$set": {"state": "matched"}}
    #     )

    #     successMessage = "You have been matched! Have fun!"
    #     send_message(successMessage, person1)
    #     send_message(successMessage, person2)

    # if (inQueue == 1):
    #     global count
    #     global waitMessage
    #     global messageDict
    #     lastPerson = personsInQueue[inQueue - 1]["chat_id"]
    #     waitMessageX = waitMessage + count * "."

    #     if lastPerson in messageDict:
    #         waitDiff = datetime.datetime.now() - messageDict[lastPerson]["time"]
    #         waitTime = waitDiff.total_seconds()
    #         if waitTime <= 60:
    #             update_message(waitMessageX, lastPerson, messageDict[lastPerson]["message_id"])
    #         else:
    #             msg = "Sorry, there seems to be no one online at the moment. Try again later."
    #             chatb_collection.update_one(
    #                 queryChatId(lastPerson),
    #                 {"$set": {"state": "untethered"}}
    #             )
    #             send_message(msg, lastPerson)
    #     else:
    #         sentMessage = send_message(waitMessageX, lastPerson, '', False)
    #         messageDict[lastPerson] = {
    #             "message_id": sentMessage['result']['message_id'],
    #             "time": datetime.datetime.now()
    #         }

    #     count = (count + 1) % 3
    # else:
    #     messageDict = {}
    # print("welp")

    chatb_collection.update_one(queryChatId(
        t_id), {"$set": {"state": "queued"}})
    waitMessage = "Looking for a match..."
    send_message(waitMessage, t_id)

    pref = chatb_collection.find(
        {"chat_id": t_id})[0]["preference"]

    if pref == 0:
        match = chatb_collection.find_one({
            "$and": [
                {"state": "queued"},
                {"chat_id": {"$ne": t_id}},
                {"isMale": True}
            ]})
    elif pref == 1:
        match = chatb_collection.find_one({
            "$and": [
                {"state": "queued"},
                {"chat_id": {"$ne": t_id}},
                {"isMale": False}
            ]})
    else:
        match = chatb_collection.find_one({
            "$and": [
                {"state": "queued"},
                {"chat_id": {"$ne": t_id}}
            ]})

    print(match)
    if (match):
        match_id = match["chat_id"]
        chatb_collection.update_one(
            queryChatId(t_id),
            {"$set": {"match_id": match_id,
                      "state": "matched"}
             }
        )
        chatb_collection.update_one(
            queryChatId(match_id),
            {"$set": {"match_id": t_id,
                      "state": "matched"}
             }
        )

        time_zone = pytz.timezone('Asia/Singapore')
        date = datetime.datetime.now()
        date_sg = time_zone.localize(date)
        datetime_str = date_sg.strftime("%m/%d/%Y, %H:%M:%S")

        name1 = chatb_collection.find(
            {"chat_id": t_id})[0]["tele"]
        name2 = chatb_collection.find(
            {"chat_id": match_id})[0]["tele"]

        history = {
            "person1": t_id,
            "name1": name1,
            "person2": match_id,
            "name2": name2,
            "time": datetime_str
        }

        chatb_history.insert_one(history)

        successMessage = "You have been matched! Have fun!"
        send_message(successMessage, t_id)
        send_message(successMessage, match_id)


# @background(schedule=0)
# def train():
#     global chatbot
#     trainer = ChatterBotCorpusTrainer(chatbot)

#     trainer.train("chatterbot.corpus.english")
#     trainer.train("chatterbot.corpus.english.greetings")
#     trainer.train("chatterbot.corpus.english.conversations")

# def chatwAI(input):
#     try:
#         msg = chatbot.get_response(input).text
#     except Exception as e:
#         print(e)
#         msg = "F I'm dumb"
#     return msg

def send_message(message, chat_id, reply_markup='', notif=True):
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup,
        "disable_notification": notif
    }
    response = requests.post(
        f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendMessage", json=(data)
    )
    return response.json()


def update_message(message, chat_id, message_id, reply_markup=''):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    response = requests.post(
        f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/editMessageText", data=data
    )


def queryChatId(chat_id):
    return {"chat_id": chat_id}
