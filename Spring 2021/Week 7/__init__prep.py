from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
import MouseTools as mt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
import pickle

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

    conn.close()

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
    elif weather is not None:
        rows = c.execute(f"SELECT * FROM weather_{weather}")

    columns = [description[0] for description in rows.description]
    
    data = []

    for row in rows.fetchall():

        temp = {}

        for column, value in zip(columns, row):
            temp[column] = value

        data.append(temp)

    conn.close()

    return jsonify(data)


@app.route("/predict/<id>")
def predict(id):

    conn = sqlite3.connect("../Week 4/waits.db")
    all_models = pickle.load(open("wdw_models.pkl", "rb"))

    current_times = pd.read_sql(f"SELECT wait_time FROM details WHERE dest_id = {mt.ids.WDW_ID} and id != {id}", conn)
    current_times['wait_time'] = current_times['wait_time'].apply(lambda x: -1 if x == None else x)
    
    pred = all_models[id].predict(current_times['wait_time'].ravel().reshape(1,-1))

    conn.close()

    return jsonify({"id":id, "predicted_time": pred[0], "periods_ahead": all_models["periods_ahead"]})

    


def create_models(periods_ahead = 1):

    conn = sqlite3.connect("../Week 4/waits.db")
    details = pd.read_sql(f"SELECT * FROM details WHERE dest_id = {mt.ids.WDW_ID}", conn)

    wdw_df = pd.DataFrame()

    for i, row in details.iterrows():
        
        df = pd.read_sql(f"SELECT * FROM id_{row['id']}", conn, index_col="last_pull").drop("status", axis=1)
        df['wait_time'] = df['wait_time'].apply(lambda x: -1 if x == None else x)
        df = df.rename({"wait_time": row['id']}, axis=1)
        
        if not wdw_df.empty:
            wdw_df = wdw_df.merge(df, how="outer", left_index=True, right_index=True)
        else:
            wdw_df = df
            
    wdw_df = wdw_df.fillna(-1)


    all_models = {"periods_ahead":periods_ahead}
    for y_id in wdw_df.columns:
        this_df = wdw_df[wdw_df[y_id] != -1]
        if this_df.empty:
            continue

        X = this_df[this_df.columns.difference([y_id])].drop(this_df.index[0:periods_ahead])
        y = this_df[y_id].shift(-periods_ahead).dropna().ravel()
        
        clf = RandomForestRegressor().fit(X, y)
        all_models[y_id] = clf

    conn.close()

    pickle.dump(all_models, open("wdw_models.pkl", "wb"))

    return all_models
        
    
create_models(1)

if __name__ == "__main__":

    app.run(debug=True)
    

