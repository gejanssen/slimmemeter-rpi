#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  appDHT_v1.py
#
#  Created by MJRoBot.org
#  10Jan18

'''
	RPi WEb Server for DHT captured data with Graph plot
'''
from datetime import datetime, timedelta

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request

app = Flask(__name__)

import sqlite3

# Retrieve LAST data from database
def getLastData():
    conn = sqlite3.connect('../dsmr42.sqlite')
    curs = conn.cursor()

    total_in, total_out, timestamp = 0, 0, 0
    for row in curs.execute("SELECT `1-0:1.7.0`, `1-0:2.7.0`, `timestamp` FROM telegrams ORDER BY timestamp DESC LIMIT 1"):
        total_in = row[0].split("*")[0]
        total_out = row[1].split("*")[0]
        timestamp = row[2]
    # for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
    #     time = str(row[0])
    #     temp = row[1]
    #     hum = row[2]
    conn.close()
    return total_in, total_out, timestamp
    #return time, temp, hum


def getHistData(numSamples):
    conn = sqlite3.connect('../dsmr42.sqlite')
    curs = conn.cursor()

    curs.execute("SELECT `1-0:1.7.0`, `1-0:2.7.0` FROM telegrams ORDER BY timestamp DESC LIMIT " + str(numSamples))
    data = curs.fetchall()
    dates = []
    total_in = []
    total_out = []
    conn.close()
    for row in reversed(data):
        #dates.append(row[0])
        total_in.append(row[0])
        total_out.append(row[1])
    return total_in, total_out


def maxRowsTable():
    conn = sqlite3.connect('../dsmr42.sqlite')
    curs = conn.cursor()
    for row in curs.execute("select COUNT(id) from  telegrams"):
        maxNumberRows = row[0]
    conn.close()
    return maxNumberRows


# initialize global variables
global numSamples
global time_obj
numSamples = maxRowsTable()
if (numSamples > 101):
    numSamples = 100

# main route
@app.route("/")
def index():
    global time_obj
    #time, temp, hum = getLastData()
    total_in, total_out, timestamp = getLastData()
    print(timestamp)
    time_obj = datetime.strptime(timestamp.split(".")[0], '%Y-%m-%dT%H:%M:%S')
    templateData = {
        'time'	: str(time_obj),
        'total_in': float(total_in) * 1000,
        'total_out': float(total_out) * 1000,
        'numSamples'	: numSamples
    }
    return render_template('index.html', **templateData)


@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int (request.form['numSamples'])
    numMaxSamples = maxRowsTable()
    if numSamples > numMaxSamples:
        numSamples = (numMaxSamples -1)

    total_in, total_out, timestamp = getLastData()
    time_obj = datetime.strptime(timestamp.split(".")[0], '%Y-%m-%dT%H:%M:%S')
    templateData = {
        'time': str(time_obj),
        'total_in': float(total_in) * 1000,
        'total_out': float(total_out) * 1000,
        'numSamples': numSamples
    }
    return render_template('index.html', **templateData)


@app.route('/plot/p_in')
def plot_power_in():
    total_ins, total_outs = getHistData(numSamples)
    ys = [float(x.split("*")[0]) * 1000 for x in total_ins]
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Power consumption in Watt")
    start = time_obj - timedelta(minutes=numSamples * 5)
    axis.set_xlabel("Periode: {} - {} (5 minute intervals)".format(start.time(), time_obj.time()))
    axis.grid(True)
    xs = range(numSamples)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/p_out')
def plot_power_out():
    total_ins, total_outs = getHistData(numSamples)
    ys = [float(x.split("*")[0]) * 1000 for x in total_outs]
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Power Surplus in Watt")
    start = time_obj - timedelta(minutes=numSamples * 5)
    axis.set_xlabel("Periode: {} - {} (5 minute intervals)".format(start.time(), time_obj.time()))
    axis.grid(True)
    xs = range(numSamples)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8765, debug=False)

