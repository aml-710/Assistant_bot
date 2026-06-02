import asyncio
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters

from config import TOKEN
from models.db import create_tables
from handlers import notes
from handlers.schedule import schedule_start, schedule_handler, callback_handler
import handlers.reminders as reminders
from handlers.start import handler as start_handler, main_menu
from handlers.weather import weather_handler
from handlers.games import (
    show_games_menu,
    start_word_game,
    stop_word_game,
    handle_word_answer,
)

# --- Создаём таблицы ---
create_tables()

# --- Создаём приложение ---
app = ApplicationBuilder().token(TOKEN).build()

# --- Стартовое меню ---
app.add_handler(start_handler)


# --- Главное меню ---
async def menu_choice(update, context):
    text = update.message.text

    if text == "📅 Расписание":
        await schedule_start(update, context)

    elif text == "📝 Заметки":
        keyboard = [
            [InlineKeyboardButton("➕ Добавить", callback_data="note_add")],
            [InlineKeyboardButton("📄 Показать", callback_data="note_show")],
            [InlineKeyboardButton("❌ Удалить", callback_data="note_delete")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выбери действие с заметками:",
            reply_markup=reply_markup
        )

    elif text == "⏰ Напоминания":
        keyboard = [
            [InlineKeyboardButton("➕ Добавить", callback_data="reminder_add")],
            [InlineKeyboardButton("📄 Показать", callback_data="reminder_show")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выбери действие с напоминаниями:",
            reply_markup=reply_markup
        )

    elif text == "🌤 Погода":
        await weather_handler(update, context)

    elif text == "🎮 Игры":
        await show_games_menu(update, context)

    elif text == "🧩 Угадай слово":
        await start_word_game(update, context)

    elif text == "⏹ Остановить игру в слова":
        await stop_word_game(update, context)

    else:
        await update.message.reply_text(
            "Выбери раздел из меню!",
            reply_markup=main_menu()
        )


# --- Кнопки заметок / напоминаний ---
async def notes_button_handler(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "note_add":
        await query.edit_message_text("Напиши текст заметки, и я её сохраню")
        context.user_data["note_mode"] = "add"

    elif data == "note_show":
        await notes.show_notes_list(user_id, query=query)

    elif data == "note_delete":
        await notes.delete_notes_list(user_id, query=query)

    elif data == "reminder_add":
        await query.edit_message_text(
            "Напиши напоминание в формате: <секунды> <текст>, например: 60 Купить хлеб"
        )
        context.user_data["reminder_mode"] = "add"

    elif data == "reminder_show":
        await reminders.show_reminders_list(user_id, query=query)

    elif data.startswith("reminder_delete_"):
        reminder_id = int(data.split("_")[2])
        await reminders.delete_reminder_by_id(reminder_id, user_id)
        await query.edit_message_text(f"Напоминание #{reminder_id} удалено")
        await reminders.show_reminders_list(user_id, query=query)


# --- Обработчик просмотра заметки ---
async def view_note_handler(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    note_id = int(query.data.split("_")[2])

    await notes.view_note(note_id, user_id, query=query)


# --- Обработчик удаления заметки ---
async def delete_note_handler(update, context):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    note_id = int(query.data.split("_")[2])

    await notes.delete_note_by_id(note_id, user_id)
    await query.edit_message_text("Заметка удалена")
    await notes.delete_notes_list(user_id, query=query)


# --- Обработка текста ---
async def notes_text_handler(update, context):
    note_mode = context.user_data.get("note_mode")
    reminder_mode = context.user_data.get("reminder_mode")

    text = update.message.text

    # --- 1. РЕЖИМ ЗАМЕТОК ---
    if note_mode == "add":
        context.args = text.split()
        await notes.add_note(update, context)
        await notes.show_notes_msg(update.effective_user.id, message=update.message)

        context.user_data["note_mode"] = None  # Сбрасываем режим
        return  # Завершаем обработку

    # --- 2. РЕЖИМ НАПОМИНАНИЙ ---
    if reminder_mode == "add":
        parts = text.split()

        if len(parts) < 2 or not parts[0].isdigit():
            await update.message.reply_text(
                "Неверный формат. Используй: <секунды> <текст>, например: 60 Купить хлеб"
            )
            return  # Не сбрасываем режим, даем пользователю исправиться
        else:
            seconds = int(parts[0])
            reminder_text = " ".join(parts[1:])
            due_ts = int(time.time()) + seconds

            reminder_id = reminders.add_reminder_db(
                update.effective_user.id,
                reminder_text,
                due_ts
            )

            await update.message.reply_text(
                f"Напоминание запланировано через {seconds} секунд: {reminder_text}"
            )

            asyncio.create_task(
                reminders.schedule_reminder(
                    context.bot,
                    update.effective_chat.id,
                    reminder_id,
                    update.effective_user.id,
                    reminder_text,
                    due_ts
                )
            )

        context.user_data["reminder_mode"] = None  # Сбрасываем режим
        return

    # --- 3. НАЖАТИЕ НА КНОПКИ ГЛАВНОГО МЕНЮ ---
    menu_buttons = [
        "📅 Расписание", "📝 Заметки", "⏰ Напоминания", 
        "🌤 Погода", "🎮 Игры", "🧩 Угадай слово", "⏹ Остановить игру в слова"
    ]
    if text in menu_buttons:
        await menu_choice(update, context)
        return

    # --- 4. ИГРА В СЛОВА И ВСЁ ОСТАЛЬНОЕ ---
    await handle_word_answer(update, context)


# --- Регистрация всех обработчиков (Хэндлеров) ---
# app.add_handler(notes.add_handler) # Отключен, так как логика теперь внутри единого текстового хэндлера

app.add_handler(notes.show_handler)
app.add_handler(notes.delete_handler)
app.add_handler(reminders.handler)

app.add_handler(schedule_handler)
app.add_handler(callback_handler)

# Обработка инлайн-кнопок
app.add_handler(CallbackQueryHandler(notes_button_handler, pattern="^(note_|reminder_)(.*)$"))
app.add_handler(CallbackQueryHandler(view_note_handler, pattern="^view_note_"))
app.add_handler(CallbackQueryHandler(delete_note_handler, pattern="^delete_note_"))

# Единый обработчик текстовых сообщений
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, notes_text_handler))


# --- Точка входа для запуска проекта ---
if __name__ == "__main__":
    print("Bot launched successfully!")
    app.run_polling()