
# Module to read, parse and store in a sqlite db telegrams from
# from a dutch smart meter (slimme meter).
# Meant as a single shot to be called from a cron script.
# You need to check the exit code as this will exit on error with only a print statement.

import os
import sqlite3
import sys
import time

import serial
from DSMR50 import obis, obis2dbcol

# Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.SEVENBITS
ser.parity = serial.PARITY_EVEN
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 20
ser.port = "/dev/ttyUSB0"

db_path = 'dsmr50.1.sqlite'

def make_db(db_path):
    cmd1 = """
                create table electric
            (
                id                INTEGER not null
                    primary key autoincrement,
                created_at        TEXT,
                delivered_1       REAL,
                delivered_2       REAL,
                returned_1        REAL,
                returned_2        REAL,
                actual_delivering REAL,
                actual_returning  REAL
            );
            """
    cmd2 = """ 
            create table gas
            (
                id            INTEGER not null
                    constraint gas_pk
                        primary key autoincrement,
                created_at    TEXT,
                gas_delivered REAL
            );
            """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute(cmd1)
        cur.execute(cmd2)
        conn.commit()
    except Exception as e:
        print(f"Failed to create dbase: {e}")
        sys.exit(4)
    finally:
        conn.close()


def read_com():
    # Open COM port
    try:
        ser.open()
    except Exception as e:
        print(f"Error opening COM: {e}")
        sys.exit("Fout bij het openen van %s. Aaaaarch." % ser.name)

    read_trys = 30  # we wait 2 seconds so this will be around 60 seconds
    while read_trys:
        # Read 1 line
        try:
            p1 = ser.readline()
        except Exception as e:
            print(e)
            print("Error reading serial socket, continuing")
            if not read_trys:
                print("No start of telegram found, read timeout, quitting")
                sys.exit(1)
            else:
                read_trys = - 1
                time.sleep(10)
        else:
            p1 = p1.decode()
            print("raw", p1)
            if p1.startswith('1-3:0.2.8'):
                # start of telegram, we continue
                print("start of telegram found, continue")
                read_trys = 0
            else:
                print("No telegram start found, polling after 2 seconds")
                if not read_trys:
                    print("No start of telegram found, read timeout, quitting")
                    sys.exit(2)
                else:
                    read_trys = - 1
                    time.sleep(10)

    # If we come here we have a start of a telegram
    p1_lines = []
    runme = True
    while runme:
        p1_line = ''
        # Read 1 line
        try:
            p1 = ser.readline()
        except Exception as e:
            print(e)
            # we don't try again as this error means trouble after the above read
            sys.exit(3)
        else:
            p1 = p1.decode()

        if p1[0].isdigit():
            print(f"read => {p1}")
            p1_lines.append(p1)

        elif p1.startswith("!"):
            # end of a telegram
            print("end of telegram")
            break

    return p1_lines


def parse_telegram(telegram):
    for line in telegram:
        line = line.strip()
        if line[0].isdigit():
            # print(p1)
            key, val = line.split('(', 1)
            if key not in obis.keys():
                print(f"key {key} not found in obis, continuing")
                continue

            # power faillure doesn't look like valid values
            if '1-0:99.97.0' in key:
                # special case with possible powerfailures list, first 4 entries looks like crap
                val = val.split(')(')[4:]
                val[-1] = val[-1].strip(')')
            elif '0-1:24.2.1' in key:
                # special case for gas, key value is different
                print(f"gas key, val: {key}, {val}")
                val = val.split(')(')
                val[1] = val[1].split('*')[0]
                val[0] = f"20{val[0][0:2]}-{val[0][2:4]}-{val[0][4:6]} {val[0][6:8]}:{val[0][8:10]}:{val[0][10:12]}"
            else:
                val = val[:-1]  # loose last )
                if '*kW' in val:
                    val = val.split('*')[0]

            if type(val) is str and val.endswith('S'):
                # it's a timestamp
                val = f"20{val[0:2]}-{val[2:4]}-{val[4:6]} {val[6:8]}:{val[8:10]}:{val[0][10:12]}"
            obis[key] = val

    return obis


def store(telegram):
    db_dict = {}
    for k, v in telegram.items():
        if k in obis2dbcol.keys():
            db_dict[obis2dbcol[k]] = v
    gas_date, m3 = db_dict['gas_delivered']
    del db_dict['gas_delivered']
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO electric VALUES (NULL, :created_at, :delivered_1, :delivered_2, "
                    ":returned_1, :returned_2, :actual_delivering, :actual_returning)", db_dict)
        cur.execute("INSERT INTO gas (id, created_at, gas_delivered) VALUES(NULL, ?, ?)", (gas_date, m3))
        conn.commit()
    except Exception as e:
        print(f"Failed to commit to dbase: {e}")
        conn.rollback()
    finally:
        conn.close()


def main():

    telegram = read_com()
    if len(telegram) != 34:
        print(f"Incomplete telegram, is {len(telegram)} lines iso 34")
        sys.exit(3)

    obis_dict = parse_telegram(telegram)
    # here we fetch the values we interested in from the telegram to put into our dbase
    store(obis_dict)


if __name__ == '__main__':

    if not os.path.exists(db_path):
        make_db(db_path)

    if len(sys.argv) > 1:
        # Testing purposes
        import pprint
        with open(sys.argv[1], 'r') as f:
            lines = f.readlines()
        obis_dict = parse_telegram(lines)
        pprint.pprint(obis_dict)
        store(obis_dict)
    else:
        main()

