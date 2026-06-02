import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from models.db import connect

# DB helpers

def add_reminder_db(user_id, text, due_ts):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (user_id, text, due_ts) VALUES (?, ?, ?)", (user_id, text, due_ts))
    conn.commit()
    reminder_id = cursor.lastrowid
    conn.close()
    return reminder_id


def get_reminders(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, due_ts FROM reminders WHERE user_id=? ORDER BY due_ts", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_reminder(user_id, reminder_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, due_ts FROM reminders WHERE user_id=? AND id=?", (user_id, reminder_id))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_reminder_by_id(reminder_id, user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id=? AND user_id=?", (reminder_id, user_id))
    conn.commit()
    conn.close()


async def schedule_reminder(bot, chat_id, reminder_id, user_id, text, due_ts):
    wait = max(0, due_ts - int(time.time()))
    await asyncio.sleep(wait)
    try:
        await bot.send_message(chat_id=chat_id, text=f"⏰ Напоминание: {text}")
    except Exception:
        pass
    delete_reminder_by_id(reminder_id, user_id)


async def show_reminders_list(user_id, query=None, message=None):
    reminders = get_reminders(user_id)
    if not reminders:
        text = "У тебя нет запланированных напоминаний"
        if query:
            await query.edit_message_text(text)
        elif message:
            await message.reply_text(text)
        return

    keyboard = []
    now = int(time.time())
    lines = []
    for rid, text, due_ts in reminders:
        delay = max(0, due_ts - now)
        mins = delay // 60
        sec = delay % 60
        lines.append(f"#{rid}: {text} (через {mins}м {sec}с)")
        keyboard.append([InlineKeyboardButton(f"Удалить #{rid}", callback_data=f"reminder_delete_{rid}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    output = "Найдено напоминаний:\n" + "\n".join(lines)
    if query:
        await query.edit_message_text(output, reply_markup=reply_markup)
    elif message:
        await message.reply_text(output, reply_markup=reply_markup)


# командный формат /remind seconds text
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        seconds = int(context.args[0])
        reminder_text = " ".join(context.args[1:]).strip()
        if not reminder_text:
            raise ValueError
        due_ts = int(time.time()) + seconds
        reminder_id = add_reminder_db(update.effective_user.id, reminder_text, due_ts)
        await update.message.reply_text(f"Ок, напомню через {seconds} секунд: {reminder_text}")
        asyncio.create_task(schedule_reminder(context.bot, update.effective_chat.id, reminder_id, update.effective_user.id, reminder_text, due_ts))
    except Exception:
        await update.message.reply_text("Пример: /remind 10 Сделать дз")


handler = CommandHandler("remind", remind)