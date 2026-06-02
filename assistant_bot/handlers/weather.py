from telegram import Update
from telegram.ext import ContextTypes
from services.weather_service import get_weather, format_weather_text

async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды погода"""
    await update.message.reply_text("Загружаю информацию о погоде...")
    
    weather_data = await get_weather()
    text = format_weather_text(weather_data)
    
    await update.message.reply_text(text)
