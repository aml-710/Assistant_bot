from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

def main_menu():
    keyboard = [
        ["📅 Расписание", "⏰ Напоминания"],
        ["📝 Заметки", "🌤 Погода"],
        ["🎮 Игры"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выбери раздел:",
        reply_markup=main_menu()
    )

handler = CommandHandler("start", start)