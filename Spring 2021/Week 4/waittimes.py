import MouseTools as mt
import sqlite3
import time
import datetime
import requests
import json
from secretkey import weather_key #https://openweathermap.org/

class Waits:

    def __init__(self):

        self.DB_NAME = "./waits.db"
        self.PAUSE_TIME = 300
        self.today = str(datetime.datetime.today()).split(" ")[0] # datetime.date.today

        self.dests = [mt.Destination(mt.ids.WDW_ID), mt.Destination(mt.ids.DLR_ID)]

        self.create_details_table()
        self.create_schedules_table()
        self.create_parks_table()
        self.create_weather_table()

        self.update_park_hours()
        self.update_entertainment_schedules()
        print("Init completed")

    def main(self):

        while True:
            try:
                if self.today < str(datetime.datetime.today()).split(" ")[0]:
                    self.today = str(datetime.datetime.today()).split(" ")[0]
                    self.update_park_hours()
                    self.update_entertainment_schedules()
                    print("Daily update hours successful, time: " + str(datetime.datetime.now()))

                self.update()
                print("Update Successful")
                time.sleep(self.PAUSE_TIME)
            except Exception as e:
                print("some error")
                print(e)

    def create_details_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS details (id TEXT PRIMARY KEY, name TEXT, entityType TEXT, last_pull TEXT, last_updated TEXT, wait_time TEXT, status TEXT, dest_id TEXT)")

        conn.commit()
        conn.close()

    def create_parks_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS parks (id TEXT PRIMARY KEY, name TEXT, entityType TEXT, last_pull TEXT, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT, dest_id TEXT, coordinates TEXT)")

        conn.commit()
        conn.close()

    def create_schedules_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS schedules (id TEXT PRIMARY KEY, name TEXT, entityType TEXT, subType TEXT, last_pull TEXT, schedule TEXT, dest_id TEXT, park_id TEXT, land_id TEXT, entertainment_venue_id TEXT, primary_location_id TEXT, coordinates TEXT)")

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
                c.execute("INSERT OR REPLACE INTO details (id, name, entityType, last_pull, last_updated, wait_time, status, dest_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, body['name'], body["entityType"], current_timestamp, body["last_updated"].timestamp(), body["wait_time"], body["status"], dest.get_id(),))


        orlando_weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat=28.388195&lon=-81.569324&units=imperial&appid={weather_key}").json()
        anaheim_weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat=33.808666&lon=-117.918955&units=imperial&appid={weather_key}").json()
        c.execute("INSERT INTO weather_orlando (last_pull, weather, weather_main, weather_decription, temp, feels_like) VALUES (?, ?, ?, ?, ?, ?)", (current_timestamp, json.dumps(orlando_weather), orlando_weather['weather'][0]['main'], orlando_weather['weather'][0]['description'], orlando_weather['main']['temp'], orlando_weather['main']['feels_like'],))
        c.execute("INSERT INTO weather_anaheim (last_pull, weather, weather_main, weather_decription, temp, feels_like) VALUES (?, ?, ?, ?, ?, ?)", (current_timestamp, json.dumps(anaheim_weather), anaheim_weather['weather'][0]['main'], anaheim_weather['weather'][0]['description'], anaheim_weather['main']['temp'], anaheim_weather['main']['feels_like'],))



        conn.commit()
        conn.close()

    def update_park_hours(self):

        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        parks = self.dests[0].get_park_ids() + self.dests[1].get_park_ids()
        for id in parks:
            c.execute("CREATE TABLE IF NOT EXISTS park_{} (date TEXT PRIMARY KEY, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT)".format(id))

            park = mt.Park(id)
            operating_open, operating_close, extra_magic_open, extra_magic_close = park.get_hours()
            try:
                operating_open = operating_open.timestamp()
            except:
                pass
            try:
                operating_close = operating_close.timestamp()
            except:
                pass
            try:
                extra_magic_open = extra_magic_open.timestamp()
            except:
                pass
            try:
                extra_magic_close = extra_magic_close.timestamp()
            except:
                pass

            c.execute("INSERT OR REPLACE INTO park_{} (date, operating_open, operating_close, extra_magic_open, extra_magic_close) VALUES (?, ?, ?, ?, ?)".format(id), (self.today, operating_open, operating_close, extra_magic_open, extra_magic_close)) #removed park.get_status
            c.execute("INSERT OR REPLACE INTO parks (id, name, entityType, last_pull, operating_open, operating_close, extra_magic_open, extra_magic_close, dest_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, park.get_name(), park.get_entityType(), self.today, operating_open, operating_close, extra_magic_open, extra_magic_close, park.get_ancestor_destination_id(), json.dumps(park.get_coordinates()),)) #removed park.get_status

        evs = self.dests[0].get_entertainment_venue_ids() + self.dests[1].get_entertainment_venue_ids()
        for id in evs:
            c.execute("CREATE TABLE IF NOT EXISTS park_{} (date TEXT PRIMARY KEY, operating_open TEXT, operating_close TEXT, extra_magic_open TEXT, extra_magic_close TEXT, status TEXT)".format(id))

            ev = mt.EntertainmentVenue(id)
            operating_open, operating_close, extra_magic_open, extra_magic_close = ev.get_hours()
            try:
                operating_open = operating_open.timestamp()
            except:
                pass
            try:
                operating_close = operating_close.timestamp()
            except:
                pass
            try:
                extra_magic_open = extra_magic_open.timestamp()
            except:
                pass
            try:
                extra_magic_close = extra_magic_close.timestamp()
            except:
                pass

            c.execute("INSERT OR REPLACE INTO park_{} (date, operating_open, operating_close, extra_magic_open, extra_magic_close) VALUES (?, ?, ?, ?, ?)".format(id), (self.today, operating_open, operating_close, extra_magic_open, extra_magic_close)) # removed get_status
            c.execute("INSERT OR REPLACE INTO parks (id, name, entityType, last_pull, operating_open, operating_close, extra_magic_open, extra_magic_close, dest_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, ev.get_name(), ev.get_entityType(), self.today, operating_open, operating_close, extra_magic_open, extra_magic_close, ev.get_ancestor_destination_id(), json.dumps(ev.get_coordinates()),)) #remove get_status

        conn.commit()
        conn.close()

        

    def update_entertainment_schedules(self):

        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        entertainments = mt.ids.WDW_ENTERTAINMENT_IDS + mt.ids.DLR_ENTERTAINMENT_IDS

        for id in entertainments:
            try:
                schedule = self.get_schedule(id)
                if schedule != []:
                    enter = mt.Entertainment(id)
                    c.execute("CREATE TABLE IF NOT EXISTS schedule_{} (date TEXT PRIMARY KEY, schedule TEXT, duration TEXT)".format(id))
                    c.execute("INSERT INTO schedule_{} (date, schedule, duration) VALUES (?, ?, ?)".format(id), (self.today, json.dumps(schedule), enter.get_duration_seconds(),))
                    c.execute("INSERT OR REPLACE INTO schedules (id, name, entityType, subType, last_pull, schedule, dest_id, park_id, land_id, entertainment_venue_id, primary_location_id, coordinates) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, enter.get_name(), enter.get_entityType(), enter.get_subType(), self.today, json.dumps(schedule), enter.get_ancestor_destination_id(), enter.get_ancestor_park_id(), enter.get_ancestor_land_id(), enter.get_ancestor_entertainment_venue_id(), json.dumps(enter.get_related_location_ids()), json.dumps(enter.get_coordinates()),))
            except Exception as e:
                pass
                print(e)
                # entertainments.extend(id)
        conn.commit()
        conn.close()


    def get_schedule(self, id, date=""):
        """
        Returns a list of dictionaries of datetime objects for the specified date's schedule in the form of [{start_time, end_time}]
        date = "YYYY-MM-DD"
        If you don't pass a date, it will get today's schedule
        """

        if date == "":
            DATE = datetime.datetime.today()
        else:
            year, month, day = date.split('-')
            DATE = datetime.datetime(int(year), int(month), int(day))

        strdate = "{}-{}-{}".format(DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day)))
        data = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}".format(id, strdate), headers=mt.auth.getHeaders()).json()

        schedule = []

        try:
            for entry in data['schedules']:
                if entry['type'] == 'Performance Time':
                    this = {}
                    this['start_time'] = datetime.strptime("{} {}".format(entry['date'], entry['startTime']), "%Y-%m-%d %H:%M:%S").timestamp()
                    this['end_time'] = datetime.strptime("{} {}".format(entry['date'], entry['endTime']), "%Y-%m-%d %H:%M:%S").timestamp()
                    schedule.append(this)
        except Exception as e:
            # print(e)
            pass

        return schedule

    def __formatDate(self, num):
        """
        Formats month and day into proper format
        """
        if len(num) < 2:
            num = '0'+num
        return num

if __name__ == "__main__":

    waits = Waits()
    waits.main()
