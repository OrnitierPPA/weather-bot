import requests
from bs4 import BeautifulSoup
import json
import re

# Функция, вставляющая ':' в списка о времени. Создана, дабы избежать "1:000, 1:200" вместо "10:00, 12:00"
def f(line):
    # Если длина линии более 3 символов, между 2 и 3 цифрой ставится ':' (10:00)
    if len(line) > 3:
        return f'{line[:2]}:{line[2:]}'
    # Иначе, ':' ставится между 1 и 2 цифрами. (1:00)
    return f'{line[:1]}:{line[1:]}'

# Функция для выбора нужного города
def city(cityname, mode, area):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    city = cityname+' ' # пробел связан с особенностью HTML документа сайта, костыль, без которого не работает поиск
    link = f"https://www.gismeteo.ru/search/{city}"

    q = requests.get(url=link, headers=headers)
    result = q.text
    soup = BeautifulSoup(result, 'lxml')
    cityname = soup.find_all('div', class_='catalog-item-link')
    ashi = [] # список для всех 'a' элементов с ссылками в поиске, среди которых идёт поиск одной нужной
    for a in cityname: # цикл, который помогает вам узнать погоду в французском Париже, а не башкирском
        a = a.find_all('a', class_='link-item')
        for href in a:
            if href.find(text=re.compile(city)): # из-за наличия <i> тегов внутри <a>, нужная строк не ищется с помощью (text=city), используем костыли 
                if len(href.text) == len(city):
                    ashi.append(href)
    for link in ashi: # переходим по каждой из ссылок, пока не найдём ту, что находится в нужном нам районе
        href = link.get('href')
        q = requests.get(url=f'https://www.gismeteo.ru{href}', headers=headers)
        result = q.text
        soup = BeautifulSoup(result, 'lxml')
        areas = soup.find_all('a', class_='breadcrumbs-link')
        for i in areas:
            if i.text == area:
                link = link.get('href')
                if mode.lower() == 'завтра':
                    weather_tomorrow(link, city)
                elif mode.lower() == 'месяц':
                    weather_30(link, city)
                else:
                    weather_today(link, city)
                return print('Выполнено')
  
def weather_today(link, city):
    city = city.strip()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    
    q = requests.get(url=f'https://www.gismeteo.ru{link}', headers=headers)
    result = q.text
    soup = BeautifulSoup(result, 'lxml')
    # Собирает данные о дожде. Взависимости от содержимого строки подставляет одну из строк.
    rane_dir = [x.text for x in soup.select('div.widget-row-precipitation-bars div.row-item div.item-unit')]
    for x in range(0,8):
        if rane_dir[x] == '0':
            rane_dir[x] = f'Осадков нет ⛅'
        elif rane_dir[x] == '':
            rane_dir[x] = f'Возможен дождь(н/д кап.) 🌧️'
        else:
            rane_dir[x] = f'Возможен дождь({rane_dir[x]} кап.) 🌧️'
    
    # Собирает данные о времени, затем подставляет двоеточие между цифрами при помощи функции f
    time_dir = [x.text for x in soup.select('div.widget-row-time div.row-item span')]
    time_dir = [line.strip() for line in time_dir]
    data_time = list(map(f, time_dir))

    # Собирает данные о температуре в цельсиях
    temp_dir = [x.text for x in soup.select('div.widget-oneday span.unit_temperature_c')]

    # Объединяет ранее собранную информацию о температуре с информацие о дожде
    gen_inf = list(zip(temp_dir, rane_dir))

    # Создаёт словарь и вносит в него все собранные данные при помощи цикла
    data = {
    f'Список погоды на сегодняшний день, {city}': "\n"
    }
    
    # На каждую позицию от 0 до 7 берёт информацию из списков той же позиции
    for i in range(8):
        data[data_time[i]] = ', '.join(gen_inf[i])

    # Создаёт json файл и помещает в него словарь
    with open('weather_today.json', 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

# Работает подобно прошлой функции, но с другой ссылкой
def weather_tomorrow(link, city):
    city = city.strip()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    
    q = requests.get(url=f'https://www.gismeteo.ru{link}tomorrow/', headers=headers)
    result = q.text
    soup = BeautifulSoup(result, 'lxml')
   
    rane_dir = [x.text for x in soup.select('div.widget-row-precipitation-bars div.row-item div.item-unit')]
    for x in range(0,8):
        if rane_dir[x] == '0':
            rane_dir[x] = f'Осадков нет ⛅'
        elif rane_dir[x] == '':
            rane_dir[x] = f'Возможен дождь(н/д кап.) 🌧️'
        else:
            rane_dir[x] = f'Возможен дождь({rane_dir[x]} кап.) 🌧️'
    

    time_dir = [x.text for x in soup.select('div.widget-row-time div.row-item span')]
    time_dir = [line.strip() for line in time_dir]
    data_time = list(map(f, time_dir))

    temp_dir = [x.text for x in soup.select('div.widget-oneday span.unit_temperature_c')]

    gen_inf = list(zip(temp_dir, rane_dir))

    data = {
    f'Список погоды на завтрашний день, {city}': "\n"
    }
    
    for i in range(8):
        data[data_time[i]] = ', '.join(gen_inf[i])

    with open('weather_tomorrow.json', 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

# Работает подобно прошлой функции, но с другой ссылкой
def weather_30(link, city):
    city = city.strip()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
    }
    
    q = requests.get(url=f'https://www.gismeteo.ru{link}month/', headers=headers)
    result = q.text
    soup = BeautifulSoup(result, 'lxml')

    # Собирает данные о числах
    date = [x.text for x in soup.select('div.widget-body a.row-item div.date')]
    date_norm = []
    for line in date:
        line = ''.join(vol for vol in line if vol.isalnum())
    
        if len(line) > 2:
            if len(line) == 4:
                line = line[:1] + ' ' + line[-3:]
            else:
                line = line[:2] + ' ' + line[-3:]

        date_norm.append(line)

    date_day = []
    
    # Цикл добавляет в список date_day день и месяц
    for day in date_norm:
        if len(day) > 2:
            if day[1:][:2] == ' ':
                month = day[1:]
            else: 
                month = day[2:]
        
        month = month.strip()
        
        if len(day) <= 2:
            day = day + ' ' + month
        
        date_day.append(day)

    # Собирают минимальную и максимальную температуру
    minT = [x.text for x in soup.select('div.widget-body a.row-item div.temp div.mint span.unit_temperature_c')]
    maxT = [x.text for x in soup.select('div.widget-body a.row-item div.temp div.maxt span.unit_temperature_c')]
    
    # ссоздаёт словарь и с помощью цикла наполняеть его данными собранными ранее
    data = {
    f'Список погоды на месяц, {city}': '\n'
    }

    for i in range(42):
        data[date_day[i]] = 'макс. {0}, мин. {1}'.format(maxT[i], minT[i])

    # Создаёт json файл и помещает в него словарь
    with open('weather_30day.json', 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

def main():
    city()

if __name__ == '__main__':
    main()