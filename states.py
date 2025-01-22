from aiogram.fsm.state import State, StatesGroup


# Создаем форму класс для профиля пользователя
class UserProfile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity_level = State()
    city = State()
    calories_goal = State()

# Создаем форму класс для логирования выпитой воды
class WaterLogger(StatesGroup):
    log_water = State()