from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

nat_city_take = KeyboardButton(text = 'Погода в моём городе')
nat_city_reg = KeyboardButton(text = 'Добавить свой город')
city_weath = KeyboardButton(text = 'Узнать погоду')

key_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(nat_city_reg).add(nat_city_take).add(city_weath)

nat_today = InlineKeyboardButton(text = 'На сегодня', callback_data = 'На сегодня')
nat_tomorrow = InlineKeyboardButton(text = 'На завтра', callback_data = 'На завтра')
nat_month = InlineKeyboardButton(text = 'На месяц', callback_data = 'На месяц')

key_nat_choice = InlineKeyboardMarkup().add(nat_today).add(nat_tomorrow).add(nat_month)

city_today = KeyboardButton(text = 'На сегодня')
city_tomorrow = KeyboardButton(text = 'На завтра')
city_month = KeyboardButton(text = 'На месяц')

key_days_city = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(city_today).add(city_tomorrow).add(city_month)