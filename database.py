import sqlite3 as sq

async def db_connect() -> None:
    global db

    db = sq.connect('data.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS native_city(user_id INTEGER PRIMARY KEY, city TEXT, area TEXT)")

    db.commit()

async def native_city_create(state, user_id):

    cur = db.cursor()

    async with state.proxy() as data:
        ncity = cur.execute(f"DELETE FROM native_city WHERE user_id = {user_id}")
        ncity = cur.execute("INSERT INTO native_city (user_id, city, area) VALUES (?, ?, ?)", (data['user_id'], data['citynative'], data['areanative']))
        db.commit()

    return ncity

async def native_city_sqlite(user):
    global nat_city, area
    cur = db.cursor()

    data_native = cur.execute(f"SELECT * FROM native_city WHERE user_id = {user}")
    data_dict = data_native.fetchall()
    for data in data_dict:
        nat_city = data[1]
        area = data[2]

    