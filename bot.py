
import telebot
from telebot import types
from config import BOT_TOKEN, DAYS_OF_WEEK, HOURS, MINUTES
from logic import add_lesson, get_user_schedule

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}


# --- Главное меню ---
@bot.message_handler(commands=["start"])
def start(message):
    username = message.from_user.first_name or "студент"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📅 Мое расписание", "🧩 Добавить урок")

    bot.send_message(
        message.chat.id,
        f"Привет, {username}! 👋\n\n"
        "Я помогу тебе создать и просматривать своё расписание.\n"
        "Выбери действие ниже. ⬇️",
        reply_markup=markup,
    )


# --- Просмотр расписания ---
@bot.message_handler(func=lambda msg: msg.text == "📅 Мое расписание")
def show_schedule(message):
    schedule_text = get_user_schedule(str(message.from_user.id))
    bot.send_message(message.chat.id, schedule_text, parse_mode="Markdown")


# --- Добавление урока ---
@bot.message_handler(func=lambda msg: msg.text == "🧩 Добавить урок")
def add_lesson_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(*DAYS_OF_WEEK)
    markup.add("⬅️ Назад")

    bot.send_message(message.chat.id, "🗓 Выбери день недели:", reply_markup=markup)


# --- Выбор времени (часа) ---
@bot.message_handler(func=lambda msg: msg.text in DAYS_OF_WEEK)
def choose_day(message):
    user_state[message.from_user.id] = {"day": message.text}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add(*HOURS)
    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        f"🗓 День: *{message.text}*\nТеперь выбери час занятия:",
        parse_mode="Markdown",
        reply_markup=markup
    )


# --- Выбор минут ---
@bot.message_handler(func=lambda msg: msg.text in HOURS)
def choose_hour(message):
    user_state[message.from_user.id]["hour"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add(*MINUTES)
    markup.add("⬅️ Назад")

    bot.send_message(
        message.chat.id,
        f"⏰ Выбран час: *{message.text}:--*\nТеперь выбери минуты:",
        parse_mode="Markdown",
        reply_markup=markup
    )


# --- Ввод названия предмета ---
@bot.message_handler(func=lambda msg: msg.text in MINUTES)
def choose_minutes(message):
    user_state[message.from_user.id]["minutes"] = message.text
    bot.send_message(
        message.chat.id,
        f"🕒 Время выбрано: *{user_state[message.from_user.id]['hour']}:{message.text}*\n"
        f"Теперь напиши название предмета:",
        parse_mode="Markdown"
    )


# --- Сохранение предмета ---
@bot.message_handler(func=lambda msg: msg.text not in DAYS_OF_WEEK + HOURS + MINUTES + ["📅 Мое расписание", "🧩 Добавить урок", "⬅️ Назад"])
def save_subject(message):
    user_id = str(message.from_user.id)
    user_data = user_state.get(message.from_user.id, {})

    if not user_data.get("day") or not user_data.get("hour") or not user_data.get("minutes"):
        return

    time = f"{user_data['hour']}:{user_data['minutes']}"
    subject = message.text.strip()

    response = add_lesson(user_id, user_data["day"], time, subject)
    bot.send_message(message.chat.id, response, parse_mode="Markdown")

    # Возвращаем главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📅 Мое расписание", "🧩 Добавить урок")
    bot.send_message(message.chat.id, "Возвращаюсь в главное меню ⬇️", reply_markup=markup)

    user_state.pop(message.from_user.id, None)


# --- Кнопка "Назад" ---
@bot.message_handler(func=lambda msg: msg.text == "⬅️ Назад")
def go_back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📅 Мое расписание", "🧩 Добавить урок")
    bot.send_message(message.chat.id, "🔙 Возвращаюсь в главное меню.", reply_markup=markup)


# --- Остальные сообщения ---
@bot.message_handler(func=lambda msg: True)
def fallback(message):
    bot.send_message(message.chat.id, "Пожалуйста, используй кнопки ниже 👇")


if __name__ == "__main__":
    print("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.infinity_polling()

