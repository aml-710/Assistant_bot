import os
from dotenv import load_dotenv

# Загружает переменные из файла .env (нужно только для локального запуска)
load_dotenv()

# os.getenv сначала ищет переменную в системе (на Railway), 
# а если не находит — берет из локального .env или использует дефолтное значение
TOKEN = os.getenv("TOKEN", "8782484643:AAGKLjJ86gDiYVIZIdPSPh3cYo_KGkUnd10")