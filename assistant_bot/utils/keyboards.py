from telegram import ReplyKeyboardMarkup

def main_menu():
    keyboard = [
        ["📅 Расписание", "⏰ Напоминания"],
        ["📝 Заметки", "🌤 Погода"],
        ["🎮 Игры"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)