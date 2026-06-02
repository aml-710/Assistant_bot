import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

SCHEDULE = {
    "Понедельник": [
        {"time": "08:15-09:35", "subject": "Социология", "room": "35", "teacher": "Едылбаева Б.М."},
        {"time": "09:45-11:05", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "11:25-12:45", "subject": "Графика", "room": "2к", "teacher": "Акжолов Д.К."},
        {"time": "12:55-14:15", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
    ],
    "Вторник": [
        {"time": "08:15-09:35", "subject": "Социология", "room": "2", "teacher": "Едылбаева Б.М."},
        {"time": "09:45-11:05", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "11:25-12:45", "subject": "Физра", "room": "с/з", "teacher": "Манат А.М."},
        {"time": "12:55-14:15", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
    ],
    "Среда": [
        {"time": "08:15-9:35", "subject": "Физра", "room": "с/з", "teacher": "Манат А.М."},
        {"time": "09:45-11:05", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "11:25-12:45", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
    ],
    "Четверг": [
        {"time": "09:45-11:05", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "11:25-12:45", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "12:55-14:15", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "14:20-15:40", "subject": "Графика", "room": "2к", "teacher": "Акжолов Д.К."},
    ],
    "Пятница": [
        {"time": "8:15-9:35", "subject": "Графика", "room": "2к", "teacher": "Акжолов Д.К."},
        {"time": "09:45-11:05", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
        {"time": "11:25-12:45", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."},
    ],
}

CALLS = ["08:15-09:35", "09:45-11:05", "11:25-12:45", "12:55-14:15", "14:20-15:40"]


def get_thursday_third_pair():
    week_number = datetime.date.today().isocalendar()[1]
    if week_number % 2 == 1:
        return {"time": "11:25-12:45", "subject": "Програмирование", "room": "11", "teacher": "Сагайдак Е.А."}
    return {"time": "11:25-12:45", "subject": "Социология", "room": "2", "teacher": "Едылбаева Б.М."}

async def schedule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(day, callback_data=day)] for day in SCHEDULE.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери день недели:", reply_markup=reply_markup)

async def day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = query.data

    text = f"📅 Расписание на {day}:\n\n"
    day_schedule = list(SCHEDULE.get(day, []))

    if day == "Четверг":
        th_pair = get_thursday_third_pair()
        found = False
        for i, item in enumerate(day_schedule):
            if item.get("time") == "11:25-12:45":
                day_schedule[i] = th_pair
                found = True
                break
        if not found:
            day_schedule.insert(1, th_pair)

    if not day_schedule:
        text += "⚠️ Расписание на этот день не задано."
    else:
        for index, item in enumerate(day_schedule, start=1):
            text += f"{index}. {item['time']} — {item['subject']} | Кабинет {item['room']} | {item['teacher']}\n"

    await query.edit_message_text(text)

schedule_handler = CommandHandler("schedule", schedule_start)
callback_handler = CallbackQueryHandler(day_callback, pattern="^(Понедельник|Вторник|Среда|Четверг|Пятница|Суббота|Воскресенье)$")