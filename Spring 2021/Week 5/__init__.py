from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)


@app.route("/")
def index():

    return "Hello World"

@app.route("/site")
def site():

    return render_template("index.html", title="Test Title")

@app.route("/site2")
def site2():

    return render_template("otherpage.html")


@app.route("/current-data")
@app.route("/current-data/<id>")
def current_data(id=None):

    # import pathlib
    # print(pathlib.Path().absolute())
    conn = sqlite3.connect("Spring 2021/Week 4/waits.db")
    c = conn.cursor()

    if id is None:
        rows = c.execute("SELECT * FROM details")
    else:
        rows = c.execute("SELECT * FROM details WHERE id = ?", (id,))

    columns = [description[0] for description in rows.description]
    
    data = []

    for row in rows.fetchall():

        temp = {}

        for column, value in zip(columns, row):
            temp[column] = value

        data.append(temp)


    return jsonify(data)



@app.route("/all-data/id/<id>")
@app.route("/all-data/park/<park>")
@app.route("/all-data/weather/<weather>")
def all_data(id=None, park=None, weather=None):

    # import pathlib
    # print(pathlib.Path().absolute())
    conn = sqlite3.connect("Spring 2021/Week 4/waits.db")
    c = conn.cursor()

    if id is not None:
        rows = c.execute(f"SELECT * FROM id_{id}")
    elif park is not None:
        rows = c.execute(f"SELECT * FROM park_{park}")
    elif location is not None:
        rows = c.execute(f"SELECT * FROM weather_{weather}")

    columns = [description[0] for description in rows.description]
    
    data = []

    for row in rows.fetchall():

        temp = {}

        for column, value in zip(columns, row):
            temp[column] = value

        data.append(temp)


    return jsonify(data)

if __name__ == "__main__":

    app.run(debug=True)