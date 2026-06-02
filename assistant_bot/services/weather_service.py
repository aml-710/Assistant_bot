import requests
from datetime import datetime

# Координаты Павлодара
PAVLODAR_LAT = 52.2830
PAVLODAR_LON = 76.9365
CITY_NAME = "Павлодар"

async def get_weather():
    """Получает подробную информацию о погоде в Павлодаре"""
    try:
        # Используем open-meteo API (бесплатный, не требует ключа)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": PAVLODAR_LAT,
            "longitude": PAVLODAR_LON,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
            "timezone": "Asia/Almaty"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "current" not in data:
            return None
        
        current = data["current"]
        
        # Интерпретация кода погоды
        weather_codes = {
            0: "Ясно ☀️",
            1: "Облачно ☁️",
            2: "Облачно ☁️",
            3: "Облачно ☁️",
            45: "Туман 🌫️",
            48: "Туман 🌫️",
            51: "Морось 🌧️",
            53: "Морось 🌧️",
            55: "Морось 🌧️",
            61: "Дождь 🌧️",
            63: "Дождь 🌧️",
            65: "Дождь 🌧️",
            71: "Снег ❄️",
            73: "Снег ❄️",
            75: "Снег ❄️",
            77: "Снег ❄️",
            80: "Дождь 🌧️",
            81: "Дождь 🌧️",
            82: "Дождь 🌧️",
            85: "Снег ❄️",
            86: "Снег ❄️",
            95: "Гроза ⛈️",
            96: "Гроза ⛈️",
            99: "Гроза ⛈️",
        }
        
        weather_desc = weather_codes.get(current["weather_code"], "Неизвестно")
        
        weather_info = {
            "temp": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind_speed": current["wind_speed_10m"],
            "wind_direction": current["wind_direction_10m"],
            "precipitation": current["precipitation"],
            "weather": weather_desc
        }
        
        return weather_info
    
    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return None

def format_weather_text(weather_data):
    """Форматирует данные погоды в красивое сообщение"""
    if not weather_data:
        return "Не удалось получить информацию о погоде"
    
    wind_directions = {
        "N": "Северный",
        "NE": "Северо-восточный",
        "E": "Восточный",
        "SE": "Юго-восточный",
        "S": "Южный",
        "SW": "Юго-западный",
        "W": "Западный",
        "NW": "Северо-западный"
    }
    
    # Определяем направление ветра по углу
    angle = weather_data["wind_direction"]
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    direction_idx = round(angle / 45) % 8
    wind_dir = wind_directions.get(directions[direction_idx], "Неизвестно")
    
    text = f"""🌍 ПОГОДА В {CITY_NAME.upper()}

{weather_data['weather']}

📊 ОСНОВНАЯ ИНФОРМАЦИЯ:
🌡️ Температура: {weather_data['temp']}°C
🤔 Ощущается как: {weather_data['feels_like']}°C
💧 Влажность: {weather_data['humidity']}%

💨 ВЕТЕР:
🌬️ Скорость: {weather_data['wind_speed']} км/ч
🧭 Направление: {wind_dir}

☔ ОСАДКИ:
💧 Количество: {weather_data['precipitation']} мм

⏰ Время обновления: {datetime.now().strftime('%H:%M:%S')}
    """
    return text
