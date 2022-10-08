from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    cityname = State()
    area = State()
    botmode = State() 

class Nativecity(StatesGroup):
    citynative = State()
    areanative = State()