import datetime
import re

from flask import Flask, render_template, request
import sqlite3
import json

app = Flask(__name__)

numSamples = 100

def getDatetimeObject(iso_string):
    timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', iso_string)
    dt = datetime.datetime.strptime(timestamp, "%Y%m%dT%H%M%S.%f%z")
    return dt


@app.route("/data.json")
def data():
    global numSamples
    conn = sqlite3.connect('../dsmr50.sqlite')
    curs = conn.cursor()
    if numSamples == 0:
        curs.execute("select COUNT(id) from  telegrams")
        numSamples = curs.fetchall()[0][0]

    curs.execute("SELECT `1-0:1.7.0`, `timestamp` FROM telegrams ORDER BY timestamp DESC LIMIT " + str(numSamples))
    data = curs.fetchall()
    #datalist = [(float(v.split('*')[0]), str(getDatetimeObject(ts).time())) for v, ts in data if '*' in v]
    datalist = [(str(getDatetimeObject(ts)), float(v.split('*')[0])) for v, ts in data if '*' in v]
    print(datalist)
    return json.dumps(datalist)


@app.route("/graph")
def graph():
    return render_template('graph.html')


if __name__ == '__main__':
    app.run(
        debug=True,
        threaded=True,
        host='127.0.0.1'
    )
