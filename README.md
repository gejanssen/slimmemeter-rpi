# Slimme meter info
Code is forked from: https://github.com/gejanssen/slimmemeter-rpi  
Webserver based of: https://medium.com/@rovai/from-data-to-graph-a-web-jorney-with-flask-and-sqlite-6c2ec9c0ad0  
Telegram codes and explanation: http://domoticx.com/p1-poort-slimme-meter-hardware/  

## Korte uitleg over slimme meters (Taken from domotix)
### Wat is een P1 poort?
De P1 poort is een seriele poort (is optioneel) op je digitale elektra meter waarin je een RJ-11 (Registered Jack) 
stekkertje kan steken (bekend van de telefoonaansluitingen) om zo de meterstanden en het verbruik uit te lezen. 
Het is niet mogelijk om gegevens naar de poort te sturen!
Onderaan deze pagina heb ik de informatiebladen “Dutch Smart Meter Requirements” (DSMR) toegevoegd.

### Niet standaard (zie DSMR v4.04, Hfdst 4.6 “signals”)
Deze seriele poort is echter niet standaard, ondanks dat hij op UART TTL niveau werkt, zijn de logische 
waarden omgedraaid: 1=0 en 0=1 ,dit is softwarematig op te lossen, maar geeft niet altijd het gewenste resultaat, 
oplossing is om dit hardwarematig te doen, bijvoorbeeld met een chip ertussen te plaatsen vaak wordt
een MAX232 of 7404 gebruikt.
Volgens de specificatie kan de poort max. 15v aan, dus een echt RS232 signaal (+12v) vanuit een “echte” com poort 
moet hij aan kunnen.
De P1 poort stuurt alleen maar data als de RTS pin is voorzien van >+5v ten opzichte van de GND (-),
zolang de spanning daarop blijft staan wordt er elke 10 seconden een “telegram” verzonden op de TxD

### Voorbeeld van een telegram, zie test-telegram.txt
Dit voorbeeld is van een Landis 350 DSRM4.2

## Connect to the meter
To connect to the meter you need a serial2usb cable.  
Not a normal one but a special cable. You can make it yourself, search the internet if you fancy some soldering.  
I just buy it on aliexpress :-)  
Search for "Dutch Smart Meter" and you have a cable for 5 euros :-)  
Make sure to include your type of meter as there are differences between various meters.  
Also check the reviews for dutch reviewers to make sure you will get a working cable for your meter.

## Code dependencies:
flask
matplotlib
serial

## Pull the meter for a telegram
We use a crontab to pull every 5 minutes a new telegram from the meter.  
(Uncomment the last part to get some output for testing)  
```*/5 * * * * /home/pi/slimmemeter-rpi/pull.sh #>>/tmp/cronrun 2>&1```

## Setup server as a systemd service
To start the flask server use the systemd service.  
(make sure start_server.sh is chmod a+x)  
```
cp appWebserver.service to /etc/systemd/system/

pi@raspberrypi:~ $ sudo systemctl start appWebserver
pi@raspberrypi:~ $ sudo systemctl status appWebserver
● appWebserver.service - Flask Webserver
   Loaded: loaded (/etc/systemd/system/appWebserver.service; disabled; vendor preset: enabled)
   Active: active (running) since Wed 2019-10-30 15:10:18 CET; 8s ago
 Main PID: 11334 (bash)
   Memory: 18.8M
   CGroup: /system.slice/appWebserver.service
           ├─11334 bash /home/pi/slimmemeter-rpi/start_server.sh
           └─11335 python3 appWebserverHist.py

okt 30 15:10:18 raspberrypi systemd[1]: Started Flask Webserver.
pi@raspberrypi:~ $

And enable it so that systemd will make it part of the setup
pi@raspberrypi:~ $ sudo systemctl enable appWebserver
Created symlink /etc/systemd/system/multi-user.target.wants/appWebserver.service → /etc/systemd/system/appWebserver.service.
pi@raspberrypi:~ $
```

## Example of the flask webpage
![Screenshot](https://raw.githubusercontent.com/schoolsplay/slimmemeter-rpi/master/out.png)
