import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")

WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")

if not WEATHER_TOKEN:
    raise ValueError("Переменная окружения WEATHER_TOKEN не установлена!")

CITY_TOKEN = os.getenv("CITY_TOKEN")

if not CITY_TOKEN:
    raise ValueError("Переменная окружения CITY_TOKEN не установлена!")