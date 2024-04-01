import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import os
from dotenv import load_dotenv
import json
import api
import time
import threading
time.sleep(5)

# load_dotenv()
API_KEY = os.environ("API_KEY")
token = os.environ("token")
bot=telebot.TeleBot(token)
maps_images = {
    "de_nuke":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/7197a969-81e4-4fef-8764-55f46c7cec6e_1695819158849.jpeg",
    "de_mirage":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/7fb7d725-e44d-4e3c-b557-e1d19b260ab8_1695819144685.jpeg",
    "de_overpass":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/058c4eb3-dac4-441c-a810-70afa0f3022c_1695819170133.jpeg",
    "de_vertigo":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/3bf25224-baee-44c2-bcd4-f1f72d0bbc76_1695819180008.jpeg",   
    "de_ancient":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/5b844241-5b15-45bf-a304-ad6df63b5ce5_1695819190976.jpeg",
    "de_inferno":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/993380de-bb5b-4aa1-ada9-a0c1741dc475_1695819220797.jpeg",
    "de_anubis":"https://assets.faceit-cdn.net/third_party/games/ce652bd4-0abb-4c90-9936-1133965ca38b/assets/votables/31f01daf-e531-43cf-b949-c094ebc9b3ea_1695819235255.jpeg"
}
def load_data(file_name: str) -> dict:
    """Функция загрузки данных из json"""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}
    
def save_data(file_name: str, data: dict):
    """Функция сохранения данных в json"""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
users = load_data("users.json")

def send_profile(chat_id: int|str, nickname: str):
    profile = api.get_profile(nickname) 
    bot.send_photo(chat_id, photo=profile["avatar"],caption=f"Nickname: {profile['nickname']}\nLevel: {profile['level']}\nElo: {profile['elo']}")

@bot.message_handler(commands=['start'])
def start_message(message):
    if True:#str(message.chat.id) not in users:
        bot.send_message(message.chat.id,"Привет, я бот который собирают твою статистку по кс2 на фасике.\nМне кажется ты кажется тут в первый раз\nДавай объясню что к чему?\n")
        users[str(message.chat.id)] = {}
        save_data("users.json", users)
        bot.send_message(message.chat.id, "Для начала введи свой ник на faceit")
        bot.register_next_step_handler(message, get_nickname_and_create_profile)
    else:
        bot.send_message(message.chat.id,"Мы вроде уже здоровались)")


def get_nickname_and_create_profile(message):
    nickname = message.text
    if api.check_nickname(nickname):
        send_profile(message.chat.id, nickname)
        users[str(message.chat.id)] = api.get_profile(nickname)
        users[str(message.chat.id)]["last_match"] = api.get_last_match(users[str(message.chat.id)]["player_id"])
        save_data("users.json", users)
        bot.send_message(message.chat.id, "Это твой профиль?")
        bot.register_next_step_handler(message, confirm_profile)
    else:
        bot.send_message(message.chat.id, "Либо ты указал не правильно свой никнейм, либо в данный момент сервис не доступен")


def confirm_profile(message):
    if message.text.lower() == "да":
        save_data("users.json", users)
        bot.send_message(message.chat.id, "Вот твой последний матч:")
        bot.register_next_step_handler(message, send_last_match(str(message.chat.id)))
        bot.send_message(message.chat.id, "Дальше я буду после каждого матча присылать твою статистику")
    elif message.text.lower() == "нет":
        bot.send_message(message.chat.id, "Давай попробуем еще разок")
        bot.send_message(message.chat.id, "Введи свой ник на faceit")
        bot.register_next_step_handler(message, get_nickname_and_create_profile)
    else:
        bot.send_message(message.chat.id, "Я тебя не понял ")
        bot.send_message(message.chat.id, "Давай попробуем еще разок")
        bot.send_message(message.chat.id, "Введи свой ник на faceit")
        bot.register_next_step_handler(message, get_nickname_and_create_profile)
        

def check_last_match():
    global users
    start_time = time.time()
    while True:
        passed_time = time.time() - start_time
        if passed_time>=60:
            for user in users:
                if "player_id" in users[user]:
                    response = api.get_last_match(users[user]["player_id"])
                    if users[user]["last_match"]["Match Id"] != response["Match Id"]:
                        users[user]["last_match"] = response
                        send_last_match(user)
            start_time = time.time()
            save_data("users.json", users)
        


def send_last_match(chat_id: int|str):
    last_match = users[str(chat_id)]["last_match"]
    text = f'''{last_match["Map"]}
{"Win" if last_match["Result"]=="1" else "Lose"}   {last_match["Score"]}
Kills: {last_match["Kills"]} 
Deaths: {last_match["Deaths"]} 
K/D Ratio: {last_match["K/D Ratio"]}
Headshots %: {last_match["Headshots %"]}
K/R Ratio: {last_match["K/R Ratio"]}
Match: {"https://www.faceit.com/ru/cs2/room/"+last_match["Match Id"]}
'''
    bot.send_photo(chat_id, photo=maps_images[last_match["Map"]],caption=text)



def polling_thread():
    bot.infinity_polling()

# thread = threading.Thread(target=some_function)
# thread.start()
thread = threading.Thread(target=check_last_match)
thread.start()

polling_thread = threading.Thread(target=polling_thread)
polling_thread.start()
# while True:
#     try:
#         check_last_match()
#         bot.infinity_polling()
#     except Exception as e:
#         print(f"Ошибка: {e}")
# if __name__ == "__main__":
#     try:
#         bot.polling()
#     except Exception as ex:
#         print("Прервано, ", ex)
#     finally:
#         save_data("users.json", users)