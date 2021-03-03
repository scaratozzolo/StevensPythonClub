import MouseTools as mt
import sqlite3
import time
import datetime
import requests
import json
from secretkey import weather_key

class Waits:

    def __init__(self):

        self.DB_NAME = "./waits.db"
        self.PAUSE_TIME = 300
        self.today = str(datetime.datetime.today()).split(" ")[0] # datetime.date.today

        self.dests = [mt.Destination(mt.ids.WDW_ID), mt.Destination(mt.ids.DLR_ID)]

        self.create_details_table()
        self.create_parks_table()
        self.create_weather_table()

    def main(self):

        while True:
            self.update()
            print("Update successful")
            time.sleep(self.PAUSE_TIME)

    def create_details_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS details (id TEXT PRIMARY KEY, name TEXT, last_pull TEXT, last_updated TEXT, wait_time TEXT, status TEXT)")

        conn.commit()
        conn.close()

    def create_parks_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS parks (id TEXT PRIMARY KEY, name TEXT, last_pull TEXT, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT, dest_id TEXT, coordinates TEXT)")

        conn.commit()
        conn.close()

    def create_weather_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS weather_orlando (last_pull TEXT PRIMARY KEY, weather TEXT, weather_main TEXT, weather_decription TEXT, temp TEXT, feels_like TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS weather_anaheim (last_pull TEXT PRIMARY KEY, weather TEXT, weather_main TEXT, weather_decription TEXT, temp TEXT, feels_like TEXT)")

        conn.commit()
        conn.close()

    def update(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        for dest in self.dests:

            wait_times = dest.get_wait_times_detailed()
            current_timestamp = datetime.datetime.now().timestamp()

            for id, body in wait_times.items():
                c.execute(f"CREATE TABLE IF NOT EXISTS id_{id} (last_pull TEXT PRIMARY KEY, wait_time TEXT, status TEXT)")

                c.execute(f"INSERT INTO id_{id} (last_pull, wait_time, status) VALUES (?, ?, ?)", (current_timestamp, body['wait_time'], body['status'],))
                c.execute("INSERT OR REPLACE INTO details (id, name, last_pull, last_updated, wait_time, status) VALUES (?, ?, ?, ?, ?, ?)", (id, body['name'], current_timestamp, body["last_updated"].timestamp(), body["wait_time"], body["status"],))



        orlando_weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat=28.388195&lon=-81.569324&units=imperial&appid={weather_key}").json()
        anaheim_weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat=33.808666&lon=-117.918955&units=imperial&appid={weather_key}").json()
        c.execute("INSERT INTO weather_orlando (last_pull, weather, weather_main, weather_decription, temp, feels_like) VALUES (?, ?, ?, ?, ?, ?)", (current_timestamp, json.dumps(orlando_weather), orlando_weather['weather'][0]['main'], orlando_weather['weather'][0]['description'], orlando_weather['main']['temp'], orlando_weather['main']['feels_like'],))
        c.execute("INSERT INTO weather_anaheim (last_pull, weather, weather_main, weather_decription, temp, feels_like) VALUES (?, ?, ?, ?, ?, ?)", (current_timestamp, json.dumps(anaheim_weather), anaheim_weather['weather'][0]['main'], anaheim_weather['weather'][0]['description'], anaheim_weather['main']['temp'], anaheim_weather['main']['feels_like'],))



        conn.commit()
        conn.close()



if __name__ == "__main__":

    waits = Waits()
    waits.main()