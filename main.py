import telebot
import json
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

# --- НАСТРОЙКИ ---
DATA_FILE = "user_data.json"
CO2_PER_KM = 0.15
RUB_PER_KM = 6
MAX_KM_LIMIT = 40  # Анти-чит: больше 40 км за раз нельзя

# --- ЗАГРУЗКА И СОХРАНЕНИЕ ---
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

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 "Привет! Это эко-бот с таблицей лидеров! 🏆\n\n"
                 "🚶‍♂️ Напиши /eco [км], чтобы записать прогулку.\n"
                 "📊 Напиши /top, чтобы увидеть лучших.\n"
                 "📉 Напиши /status, чтобы увидеть свой результат.")

@bot.message_handler(commands=['eco'])
def calculate_eco(message):
    try:
        args = message.text.split()
        
        if len(args) < 2:
            bot.reply_to(message, "Напиши, сколько прошел. Например: /eco 5")
            return

        km = float(args[1])
        
        # --- АНТИ-ЧИТ ---
        if km <= 0:
            bot.reply_to(message, "Расстояние должно быть больше нуля!")
            return
        if km > MAX_KM_LIMIT:
            bot.reply_to(message, "Эй, не читери! 40 км за раз пешком пройти сложно. Вводи частями.")
            return
        # ----------------
        
        saved_co2 = km * CO2_PER_KM
        saved_money = km * RUB_PER_KM
        
        user_id = str(message.from_user.id)
        user_name = message.from_user.first_name # Берем имя из Телеграма
        
        if user_id not in user_stats:
            user_stats[user_id] = {'co2': 0.0, 'money': 0.0, 'name': user_name}
        
        # Обновляем имя (если вдруг поменял) и статистику
        user_stats[user_id]['name'] = user_name
        user_stats[user_id]['co2'] += saved_co2
        user_stats[user_id]['money'] += saved_money
        
        save_data()
        
        bot.reply_to(message, 
                     f"Записал! +{km} км.\n"
                     f"Природа говорит спасибо: {saved_co2:.2f} кг CO2\n"
                     f"Твой кошелек рад: {saved_money:.0f} руб.")
        
    except ValueError:
        bot.reply_to(message, "Пиши цифрами. Например: /eco 4.5")

@bot.message_handler(commands=['status'])
def send_status(message):
    user_id = str(message.from_user.id)
    
    if user_id in user_stats:
        data = user_stats[user_id]
        bot.reply_to(message, 
                     f"👤 Статистика для {data.get('name', 'User')}:\n"
                     f"🌿 CO2: {data['co2']:.2f} кг\n"
                     f"💰 Деньги: {data['money']:.0f} руб.")
    else:
        bot.reply_to(message, "Ты еще ничего не прошел. Напиши /eco")

@bot.message_handler(commands=['top'])
def send_top(message):
    if not user_stats:
        bot.reply_to(message, "Список лидеров пока пуст.")
        return

    # Сортировка: берем всех пользователей и сортируем по CO2 (от большего к меньшему)
    sorted_users = sorted(user_stats.items(), key=lambda item: item[1]['co2'], reverse=True)
    
    # Берем только топ-5
    top_5 = sorted_users[:5]
    
    text = "🏆 ТОП-5 ЭКО-ГЕРОЕВ:\n\n"
    for i, (uid, data) in enumerate(top_5, 1):
        name = data.get('name', 'Аноним')
        score = data['co2']
        text += f"{i}. {name} — {score:.2f} кг CO2\n"
        
    bot.reply_to(message, text)

@bot.message_handler(commands=['reset_full_data'])
def reset_data(message):
    user_id = str(message.from_user.id)
    if user_id in user_stats:
        # Обнуляем только цифры, имя оставляем
        user_stats[user_id]['co2'] = 0.0
        user_stats[user_id]['money'] = 0.0
        save_data()
        bot.reply_to(message, "Статистика сброшена.")
    else:
        bot.reply_to(message, "Нечего сбрасывать.")

if __name__ == '__main__':
    print("Бот с таблицей лидеров запущен...")
    bot.polling(none_stop=True)
