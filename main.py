import telebot
import json
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


DATA_FILE = "user_data.json"
CO2_PER_KM = 0.15
RUB_PER_KM = 6


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_stats, f, ensure_ascii=False, indent=4)
    except:
        pass 

user_stats = load_data()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "Привет! Это мой бот для проекта.\n"
                 "Он считает, сколько ты сэкономил CO2 и денег, когда идешь пешком.\n\n"
                 "Просто напиши /eco и число километров.\n"
                 "Например: /eco 3")

@bot.message_handler(commands=['eco'])
def calculate_eco(message):
    try:
        args = message.text.split()
        
        if len(args) < 2:
            bot.reply_to(message, "Напиши, сколько прошел. Типа так: /eco 5")
            return

        km = float(args[1])
        
        saved_co2 = km * CO2_PER_KM
        saved_money = km * RUB_PER_KM
        
        user_id = str(message.from_user.id)
        
        if user_id not in user_stats:
            user_stats[user_id] = {'co2': 0.0, 'money': 0.0}
        
        user_stats[user_id]['co2'] += saved_co2
        user_stats[user_id]['money'] += saved_money
        
        save_data()
        
        bot.reply_to(message, 
                     f"Ты прошел {km} км. Круто!\n"
                     f"Воздух чище на: {saved_co2:.2f} кг CO2\n"
                     f"Твоя экономия: {saved_money:.0f} руб.")
        
    except ValueError:
        bot.reply_to(message, "Пиши цифрами, а не буквами. Например: /eco 4.5")

@bot.message_handler(commands=['status'])
def send_status(message):
    user_id = str(message.from_user.id)
    
    if user_id in user_stats:
        total_co2 = user_stats[user_id]['co2']
        total_money = user_stats[user_id]['money']
        bot.reply_to(message, 
                     f"Твой общий результат:\n"
                     f"Всего спас природы: {total_co2:.2f} кг CO2\n"
                     f"Сэкономил денег: {total_money:.0f} руб.")
    else:
        bot.reply_to(message, "Статистики пока нет. Сходи погулять и напиши /eco")

@bot.message_handler(commands=['reset_full_data'])
def reset_data(message):
    user_id = str(message.from_user.id)
    if user_id in user_stats:
        user_stats[user_id] = {'co2': 0.0, 'money': 0.0}
        save_data()
        bot.reply_to(message, "Всё сбросил. Статистика пустая.")
    else:
        bot.reply_to(message, "Тут и так пусто.")

if __name__ == '__main__':
    print("Бот работает...")
    bot.polling(none_stop=True)
