import random
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import ContextTypes

WORD_QUESTIONS = [
    {"question": "Язык программирования, начинающийся на P", "answer": "python"},
    {"question": "Команда в Python для вывода текста", "answer": "print"},
    {"question": "Структура данных в Python в квадратных скобках", "answer": "список"},
    {"question": "Фигура с тремя сторонами", "answer": "треугольник"},
    {"question": "Результат умножения", "answer": "произведение"},
    {"question": "То, что хранит данные в программе", "answer": "переменная"},
    {"question": "Наука о числах и формулах", "answer": "математика"},
    {"question": "Устройство для управления курсором", "answer": "мышь"},
    {"question": "Команда для создания функции в Python", "answer": "def"},
    {"question": "Главная страница сайта", "answer": "индекс"}
]


def games_menu():
    keyboard = [
        ["🧩 Угадай слово"],
        ["⬅ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def word_game_menu():
    keyboard = [
        ["⏹ Остановить игру в слова"],
        ["⬅ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


class WordGame:
    def __init__(self):
        self.current = None
        self.score = 0
        self.streak = 0
        self.active = False

    def start(self):
        self.score = 0
        self.streak = 0
        self.active = True
        self.next_word()

    def next_word(self):
        self.current = random.choice(WORD_QUESTIONS)

    def check_answer(self, user_answer):
        correct_answer = self.current["answer"].strip().lower()
        user_answer = user_answer.strip().lower()

        if user_answer == correct_answer:
            self.score += 1
            self.streak += 1
            return True, correct_answer
        else:
            self.streak = 0
            return False, correct_answer


word_game = WordGame()


async def show_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Выбери игру:",
        reply_markup=games_menu()
    )


async def start_word_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word_game.start()

    await update.message.reply_text(
        "Игра началась!",
        reply_markup=word_game_menu()
    )

    await send_word_question(update, context)


async def send_word_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = word_game.current
    answer_len = len(q["answer"])

    await update.message.reply_text(
        f"🧩 Угадай слово\n\n"
        f"Вопрос: {q['question']}\n"
        f"Количество букв: {answer_len}"
    )


async def stop_word_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word_game.active = False

    await update.message.reply_text(
        f"Игра остановлена\n"
        f"Очки: {word_game.score}\n"
        f"Серия: {word_game.streak}"
    )


async def handle_word_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not word_game.active:
        return

    user_text = update.message.text

    if user_text in ["🧩 Угадай слово", "⏹ Остановить игру в слова", "⬅ Назад"]:
        return

    result, correct_answer = word_game.check_answer(user_text)

    if result:
        await update.message.reply_text(
            f"✅ Правильно!\n"
            f"Серия: {word_game.streak}\n"
            f"Очки: {word_game.score}"
        )
    else:
        await update.message.reply_text(
            f"❌ Неправильно\n"
            f"Правильный ответ: {correct_answer}\n"
            f"Серия сброшена"
        )

    word_game.next_word()
    await send_word_question(update, context)