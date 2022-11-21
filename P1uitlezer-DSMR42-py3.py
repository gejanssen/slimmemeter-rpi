#
# DSMR P1 uitlezer
# (c) 10-2012 2016 - GJ - gratis te kopieren en te plakken

PRODUCTION = True

from datetime import datetime
import sqlite3
from pprint import pprint

versie = "1.2-py3"
import sys
import serial


################
# Error display #
################
def show_error(mesg=''):
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
    print("Fout in %s type: %s" % (mesg, ft))
    print("Fout waarde: %s" % fv)
    return

def halt(mesg="Clean exit", ret=0):
    print(mesg)
    # Close port and show status
    try:
        ser.close()
    except:
        show_error(ser.name)
        # in *nix you should pass 0 for succes or >0 when it fails as exitr value
        sys.exit(1)
    sys.exit(ret)


##################################################
# Main program
##################################################
print("DSMR 4.2 P1 uitlezer", versie)
print("Control-C om te stoppen")

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

# Open COM port
try:
    ser.open()
except:
    show_error(ser.name)
    halt("Error opening serial socket", ret=1)

# Initialize
# stack is mijn list met de 36 regeltjes.
p1_teller = 0
t_lines = {}
db_t_lines = [None]
# Test
# with open('test-telegram.txt', 'r') as f:
#     lines = f.readlines()

while p1_teller < 36:
    p1_line = ''
    # Read 1 line
    try:
        p1 = ser.readline()
        # if lines:
        #     p1 = lines.pop(0)
        # else:
        #     break
    except Exception as e:
        print(e)
        show_error(ser.name)
        halt("Error reading serial socket", ret=2)
    else:
        p1 = p1.decode()

    #print("raw output", p1)
    if p1[0].isdigit():
        #print(p1)
        key, val = p1.strip().split('(', 1)
        db_t_lines.append(val.strip(")")) # strip the ) to get original value for dbase
        val = val[:-1] # loose last )
        if "*kW" in val:
            val = val.split('*kW')[0]
        t_lines[key] = val
    elif p1.startswith("!"):
        # end of a telegram
        break

    p1_teller = p1_teller + 1
#print(len(t_lines), "total lines")
if len(t_lines) != 30:
    halt("No valid telegram received?", ret=3)

# strore the data into the dbase first
#pprint(db_t_lines)
t = datetime.now().astimezone().isoformat()
db_t_lines.append(t)
con = sqlite3.connect('dsmr42.sqlite')
cur = con.cursor()
placeholders = ', '.join('?' * len(db_t_lines))
sql = 'INSERT INTO telegrams VALUES ({})'.format(placeholders)
#print(sql, db_t_lines)
cur.execute(sql, db_t_lines)
con.commit()

if PRODUCTION:


    sys.exit(0)

meter = 0

for key, val in t_lines.items():
    #print(key, val)
    if key == "1-0:1.8.1":
        print("{:<30s} {:<10} KW".format("totaal laagtarief verbruik", val))
        meter += int(float(val))
    elif key == "1-0:1.8.2":
        print("{:<30s} {:<10} KW".format("totaal hoogtarief verbruik", val))
        meter += int(float(val))
    elif key == "1-0:2.8.1":
        print("{:<30s} {:<10} KW".format("totaal laagtarief retour", val))
        meter -= int(float(val))
    elif key == "1-0:2.8.2":
        print("{:<30s} {:<10} KW".format("totaal hoogtarief retour", val))
        meter -= int(float(val))
    elif key == "1-0:1.7.0":
        print("{:<30s} {:<10} W".format("huidig afgenomen vermogen", float(val) * 1000))
    elif key == "1-0:2.7.0":
        print("{:<30s} {:<10} W".format("huidig teruggeleverd vermogen", float(val) * 1000))


print("{:<30s} {:<10} KW {:<10}".format("meter totaal", meter, "afgenomen/teruggeleverd van het net"))



