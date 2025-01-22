from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from typing import Any, Dict
from states import UserProfile, WaterLogger
from datetime import datetime
import aiohttp
from config import WEATHER_TOKEN, CITY_TOKEN

router = Router()

#  Класс для логирования воды
class WaterLoggerClass():
    def __init__(self):
        self.daily_water_norm = None
        self.water_consumption = 0
    
    def update_water_consumption(self, water_volume: float):
        self.water_consumption = self.water_consumption + water_volume

    def update_water_norm(self, water_norm: float):
        self.daily_water_norm = water_norm

water_logger = WaterLoggerClass()


@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(UserProfile.weight)
    await message.answer(
        "Привет! Я бот для трекинга здоровья.\nВведите Ваш вес:",
        reply_markup=ReplyKeyboardRemove(),
    )

@router.message(UserProfile.weight)
async def process_weight(message: Message, state: FSMContext) -> None:
    await state.update_data(weight=message.text)
    await state.set_state(UserProfile.height)
    await message.answer(
        f"Введите Ваш рост:",
    )

@router.message(UserProfile.height)
async def process_height(message: Message, state: FSMContext) -> None:
    await state.update_data(height=message.text)
    await state.set_state(UserProfile.age)
    await message.answer(
        f"Введите Ваш возраст:",
    )

@router.message(UserProfile.age)
async def process_age(message: Message, state: FSMContext) -> None:
    await state.update_data(age=message.text)
    await state.set_state(UserProfile.activity_level)
    await message.answer(
        f"Введите Ваш уровень активности:",
    )

@router.message(UserProfile.activity_level)
async def process_activity_level(message: Message, state: FSMContext) -> None:
    await state.update_data(activity_level=message.text)
    await state.set_state(UserProfile.city)
    await message.answer(
        f"Введите Ваш город:",
    )

@router.message(UserProfile.city)
async def process_city(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await state.set_state(UserProfile.calories_goal)
    await message.answer(
        f"Введите Вашу цель по уровню калорий:",
    )

@router.message(UserProfile.calories_goal)
async def process_calories_goal(message: Message, state: FSMContext) -> None:
    await state.update_data(calories_goal=message.text)
    await message.answer(
        f"Спасибо, Ваш профиль заполнен!",
    )
    await state.set_state(state=None)


# Функция для получения профиля пользователя
@router.message(Command("get_profile"))
async def get_profile(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    weight = data.get('weight')
    height = data.get('height')
    age = data.get('age')
    activity_level = data.get('activity_level')
    city = data.get('city')
    calories_goal = data.get('calories_goal')
    await message.answer(
        f"""Ваш вес: {weight}\n Ваш рост: {height}\n Ваш возраст: {age}
    Ваш уровень активности: {activity_level}\n Ваш город: {city}\n Ваша цель по калориям: {calories_goal}"""
    )


# Функция для расчета нормы воды
@router.message(Command("calculate_daily_water"))
async def calculate_daily_water(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    weight = int(data.get('weight'))
    height = int(data.get('height'))
    age = int(data.get('age'))
    activity_level = float(data.get('activity_level'))
    city = data.get('city')
    calories_goal = int(data.get('calories_goal'))

    # Достаем температуру по городу
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.api-ninjas.com/v1/geocoding?city={city}&country=rus",
                               headers={'X-Api-Key': CITY_TOKEN}) as response:
            result = await response.json()
            lat = result[0]['latitude']
            lon = result[0]['longitude']

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_TOKEN}",) as response:
            result = await response.json()
            temperature = result['main']['temp']
            

    water_norm = weight*30 + (500*(activity_level//30)) + 500 + 1000*(temperature>25)
    water_logger.update_water_norm(water_norm=water_norm)
    await message.answer(
        f"""Ваша дневная норма воды: {water_norm} """
    )   

    
# Функция для логирования воды
@router.message(Command("log_water"))
async def calculate_daily_water(message: Message, state: FSMContext) -> None:
    await state.set_state(WaterLogger.log_water)
    await message.answer(
        "Чтобы залогировать воду, введите объем выпитой воды в мл.:",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(WaterLogger.log_water)
async def calculate_daily_water(message: Message, state: FSMContext) -> None:
    if water_logger.daily_water_norm == None:
        await message.answer(
            """Норма воды не установлена. Пожалуйста, установите норму воды командой /calculate_daily_water"""
        )
        await state.set_state(state=None)
    else:
        await state.update_data(log_water=message.text)
        data = await state.get_data()
        water_volume = int(data['log_water'])
        water_logger.update_water_consumption(water_volume=water_volume)

        if water_logger.daily_water_norm <= water_logger.water_consumption:
            await message.answer(
                """Вода залогирована, спасибо! Ваша цель по воде выполнена!""",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(state=None)
        else:
            water_diff = water_logger.daily_water_norm - water_logger.water_consumption
            await message.answer(
                f"""Вода залогирована, спасибо! До выполнения цели по воде осталось: {water_diff} мл""",
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.set_state(state=None)