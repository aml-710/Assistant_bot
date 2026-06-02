from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from models.db import connect

# получить все заметки пользователя
def get_user_notes(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM notes WHERE user_id=? ORDER BY id", (user_id,))
    notes_list = cursor.fetchall()
    conn.close()
    return notes_list

# получить одну заметку по ID
def get_note_by_id(note_id, user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM notes WHERE id=? AND user_id=?", (note_id, user_id))
    note = cursor.fetchone()
    conn.close()
    return note

# показать список заметок с кнопками для просмотра
async def show_notes_list(user_id, query=None, message=None):
    notes_list = get_user_notes(user_id)
    
    if not notes_list:
        text = "У тебя нет заметок"
    else:
        keyboard = [[InlineKeyboardButton(f"#{note_id} {note_text[:30]}", callback_data=f"view_note_{note_id}")] 
                    for note_id, note_text in notes_list]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Выбери заметку для просмотра:"
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup)
        elif message:
            await message.reply_text(text, reply_markup=reply_markup)
        return

    if query:
        await query.edit_message_text(text)
    elif message:
        await message.reply_text(text)

# показать единственную заметку
async def view_note(note_id, user_id, query=None, message=None):
    note = get_note_by_id(note_id, user_id)
    
    if not note:
        text = "Заметка не найдена"
    else:
        text = f"Заметка #{note[0]}:\n\n{note[1]}"
    
    keyboard = [[InlineKeyboardButton("Назад", callback_data="note_show")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(text, reply_markup=reply_markup)
    elif message:
        await message.reply_text(text, reply_markup=reply_markup)

# показать список заметок с кнопками для удаления
async def delete_notes_list(user_id, query=None, message=None):
    notes_list = get_user_notes(user_id)
    
    if not notes_list:
        text = "У тебя нет заметок"
    else:
        keyboard = [[InlineKeyboardButton(f"Удалить #{note_id}: {note_text[:25]}", callback_data=f"delete_note_{note_id}")] 
                    for note_id, note_text in notes_list]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Выбери заметку для удаления:"
        
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup)
        elif message:
            await message.reply_text(text, reply_markup=reply_markup)
        return

    if query:
        await query.edit_message_text(text)
    elif message:
        await message.reply_text(text)

# добавить заметку (Универсальная функция)
async def add_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если функция вызвана через текстовый ввод (note_mode == "add"), 
    # текст лежит в update.message.text. 
    # Если через команду /addnote, то текст лежит в context.args.
    if context.args:
        text = " ".join(context.args)
    else:
        text = update.message.text

    if not text or text.startswith('/addnote'):
        await update.message.reply_text("Используй: /addnote текст заметки или просто напиши текст.")
        return

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (update.effective_user.id, text))
    conn.commit()
    conn.close()
    await update.message.reply_text("Заметка добавлена")

# показать заметки через команду /notes
async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_notes_list(update.effective_user.id, message=update.message)

# удалить заметку по ID
async def delete_note_by_id(note_id, user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, user_id))
    conn.commit()
    conn.close()

# регистрация команд
add_handler = CommandHandler("addnote", add_note)
show_handler = CommandHandler("notes", show_notes)
delete_handler = CommandHandler("delnote", show_notes)