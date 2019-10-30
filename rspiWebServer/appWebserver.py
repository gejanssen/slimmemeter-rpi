from datetime import datetime

from flask import Flask, render_template, request

app = Flask(__name__)
import sqlite3  # Retrieve data from database


def getData():
    total_in, total_out, timestamp = 0, 0, 0
    conn = sqlite3.connect('../dsmr42.sqlite')
    curs = conn.cursor()
    for row in curs.execute("SELECT `1-0:1.7.0`, `1-0:2.7.0`, `timestamp` FROM telegrams ORDER BY timestamp DESC LIMIT 1"):
        total_in = row[0].split("*")[0]
        total_out = row[1].split("*")[0]
        timestamp = row[2]
    conn.close()
    return total_in, total_out, timestamp

@app.route("/")
def index():
    total_in, total_out, timestamp = getData()
    time_obj = datetime.strptime(timestamp.split(".")[0], '%Y-%m-%dT%H:%M:%S')
    templateData = {
        'total_in': float(total_in) * 1000,
        'total_out': float(total_out) * 1000,
        'time': str(time_obj)
    }
    return render_template('index.html', **templateData)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8765, debug=False)
    #app.run(host='192.168.0.6', port=80, debug=False)
