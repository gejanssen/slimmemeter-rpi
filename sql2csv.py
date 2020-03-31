import datetime
import re
import sqlite3

dbpath = 'dsmr50.sqlite'
numSamples = 0 # meaning all entries
db_col = '1-0:1.7.0'
csv_name = 'KW-usage.csv'

def getDatetimeObject(iso_string):
    if iso_string.find('.') == -1:
        # when we don't have a decimal the datetime fails
        a, b = iso_string.split('+')
        iso_string = "{}.0+{}".format(a, b)
    timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', iso_string)
    return datetime.datetime.strptime(timestamp, "%Y%m%dT%H%M%S.%f%z")

conn = sqlite3.connect(dbpath)
curs = conn.cursor()

if numSamples == 0:
    curs.execute("select COUNT(id) from  telegrams")
    numSamples = curs.fetchall()[0][0]

print("getting {} number of samples".format(numSamples))

curs.execute("SELECT `timestamp` FROM telegrams ORDER BY timestamp ASC LIMIT 1")
timestamp_start = getDatetimeObject(curs.fetchone()[0])

curs.execute("SELECT `timestamp` FROM telegrams ORDER BY timestamp DESC LIMIT 1")
timestamp_end = getDatetimeObject(curs.fetchone()[0])

curs.execute("SELECT `{}`, `timestamp` FROM telegrams ORDER BY timestamp ASC LIMIT ".format(db_col) + str(numSamples))
data = curs.fetchall()
datalist = [(v.split('*')[0], getDatetimeObject(ts)) for v, ts in data if '*' in v]

csvlist = ""
for v, dt in datalist:
    csvlist += "{},{}_{}:{}\r\n ".format(v, dt.date(), dt.hour, dt.minute)

with open(csv_name, 'w') as f:
    f.write(csvlist)

print("Done, your list is in {}".format(csv_name))


