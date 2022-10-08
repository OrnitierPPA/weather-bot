from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, executor, types

import database, keyboards, json
from config import token
from weather import city
import states as s

storage = MemoryStorage()
bot = Bot(token = token)
dp = Dispatcher(bot, storage = storage)

async def on_startup(_):
    await database.db_connect()
    print('Подключение к БД выполнено успешно')

# Функция выводящая 
async def native_city_conclusion(mode, callback_query: types.CallbackQuery):

    user = callback_query.from_user.id
    await database.native_city_sqlite(user)

    city(database.nat_city, mode, database.area)

    if mode.lower() == 'завтра':
        with open('weather_tomorrow.json',  encoding='utf-8') as file:
            data_weather = json.load(file)

            for k, v in data_weather.items():
                weather_data = f"{k}: {v}"

                await bot.send_message(user, weather_data)
    
    elif mode.lower() == 'сегодня':
        with open('weather_today.json',  encoding='utf-8') as file:
            data_weather = json.load(file)

            for k, v in data_weather.items():
                weather_data = f"{k}: {v}"

                await bot.send_message(user, weather_data)

    elif mode.lower() == 'месяц':
        with open('weather_30day.json',  encoding='utf-8') as file:
            data_weather = json.load(file)

            for k, v in data_weather.items():
                weather_data = f"{k}: {v}"

                await bot.send_message(user, weather_data)

@dp.message_handler(commands=['start'], state = None)
async def send_welcome(message: types.Message):
    
    await message.reply('Привет!\nЧтобы узнать погоду,\nвыберите подходящую Тебе опцию.', reply_markup = keyboards.key_start)

@dp.callback_query_handler(Text("На завтра"),  state = None)
async def native_today(callback_query: types.CallbackQuery):

    mode = 'завтра'
    await native_city_conclusion(mode, callback_query)
            
@dp.callback_query_handler(Text("На сегодня"), state = None)
async def native_today(callback_query: types.CallbackQuery):

    mode = 'сегодня'
    await native_city_conclusion(mode, callback_query)

@dp.callback_query_handler(Text("На месяц"), state = None)
async def native_month(callback_query: types.CallbackQuery):

    mode = 'месяц'
    await native_city_conclusion(mode, callback_query)

@dp.message_handler(Text("Добавить свой город"), state = None)
async def native_city_reg(message: types.Message):

    await s.Nativecity.citynative.set()
    await message.reply('Назовите ваш родной город.')

@dp.message_handler(state=s.Nativecity.citynative)
async def native_city(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['citynative'] = message.text
    await s.Nativecity.next()
    await message.reply('Введите свою родную область/район/республику.')

@dp.message_handler(state=s.Nativecity.areanative)
async def select_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['areanative'] = message.text
        data['user_id'] = message.from_user.id
    
    user_id = data['user_id']
    
    await database.native_city_create(state, user_id)
    await state.finish()

@dp.message_handler(Text("Погода в моём городе"), state = None)
async def send_welcome(message: types.Message):

    await message.reply('Выберите один из вариантов:', reply_markup = keyboards.key_nat_choice)

@dp.message_handler(Text('Узнать погоду'), content_types=types.ContentTypes.TEXT)
async def start_form(message: types.Message):
    await s.Form.cityname.set()
    await message.reply('Напишите название города.')

@dp.message_handler(state=s.Form.cityname)
async def select_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['cityname'] = message.text
    await s.Form.next()
    await message.reply('Введите свою область/район/республику.')

@dp.message_handler(state=s.Form.area)
async def select_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['area'] = message.text
    await s.Form.next()
    await message.reply('На какой промежуток времени вы хотели бы узанть погоду (сегодня, завтра, месяц)?', reply_markup = keyboards.key_days_city)

@dp.message_handler(state=s.Form.botmode)
async def select_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        mode = message.text
    await state.finish() 

    city(data['cityname'], mode, data['area'])

    if mode.lower() == 'на завтра':
        with open('weather_tomorrow.json',  encoding='utf-8') as file:
            data_weather = json.load(file)

            for k, v in data_weather.items():
                weather_data = f"{k}: {v}"

                await message.answer(weather_data)

    elif mode.lower() == 'на сегодня':
        with open('weather_today.json',  encoding='utf-8') as file:
            data_weather = json.load(file)

            for k, v in data_weather.items():
                weather_data = f"{k}: {v}"

                await message.answer(weather_data)

    elif mode.lower() == 'на месяц':
        with open('weather_30day.json',  encoding='utf-8') as file:
            data_weather = json.load(file)

            for k, v in data_weather.items():
                weather_data = f"{k}: {v}"

                await message.answer(weather_data)

def main():
	executor.start_polling(dp, on_startup=on_startup)

if __name__ == '__main__':
    main()