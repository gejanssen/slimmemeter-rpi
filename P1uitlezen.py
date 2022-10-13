# DSMR P1 uitlezen
# (c) 10-2012 - GJ - gratis te kopieren en te plakken
versie = "1.0"
import sys
import serial

##############################################################################
# Main program
##############################################################################
print("DSMR P1 uitlezen (raw)", versie)
print("Control-C om te stoppen")
print("Pas eventueel de waarde ser.port aan in het python script")
input("Hit any key to start")

# Set COM port config (dsmr4.2)
# ser = serial.Serial()
# ser.baudrate = 9600
# ser.bytesize = serial.SEVENBITS
# ser.parity = serial.PARITY_EVEN
# ser.stopbits = serial.STOPBITS_ONE
# ser.xonxoff = 0
# ser.rtscts = 0
# ser.timeout = 20

# Set COM port config (dsmr 5.0)
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
except Exception as e:
    print(f"Error opening COM: {e}")
    sys.exit("Fout bij het openen van %s. Aaaaarch." % ser.name)

# Initialize
# p1_teller is mijn tellertje voor van 0 tot 20 te tellen
p1_teller = 0

f = open('telegram-dsrm50.txt', 'w')

while p1_teller < 40:
    p1_line = ''
    # Read 1 line
    try:
        p1 = ser.readline()
    except Exception as e:
        print(e)
        sys.exit("Error reading serial socket")
    else:
        p1 = p1.decode()
        print("raw", p1)
        f.write(p1)                                                                 

    if p1[0].isdigit():
        print(f"line {p1_teller} => {p1}")

    elif p1.startswith("!"):
        # end of a telegram
        break

    p1_teller = p1_teller + 1

try:
    f.close()
except:
    print("Failed to close file")

# Close port
try:
    ser.close()
except:
    sys.exit("Oops %s. Programma afgebroken. Kon de seriele poort niet sluiten." % ser.name)
