# slimmemeter-rpi
zie ook

http://gejanssen.com/howto/Slimme-meter-uitlezen/index.html
en
http://gejanssen.com/howto/rpi-rrd-power/index.html

## Installeer software

```
./packages.sh
```

Installeren van
* cu
* Python-serial

Zet de rechten van de seriele poort open. (pi is de user die toegevoegd wordt aan de dialout group)

```
gej@rpi-backup:~/slimmemeter-rpi $ sudo usermod -a -G dialout www-data pi
```

09-2016 iemand die ik ken heeft een DSMR 4.2 meter gekregen, dus heb ik alles geupdate naar een DSMR 2 en een DSMR 4 versie.
De scriptjes hebben dus een nieuwe naam.

11-2017 Update, mijn slimme meter was defekt, iets met een simkaartje wat niet meer werkte/geaccepteerd werd door de providers.
We hebben nu een ESMR 5.0 meter.

## Eerst even kijken of we serieel uit kunnen lezen met cu

DSMR 2.0
```
gej@raspberrypi:~/slimmemeter-rpi $ cu -l /dev/ttyUSB0 -s 9600 --parity=none
Connected.
/KMP5 KA6U001660297912

0-0:96.1.1(204B413655303031363630323937393132)
1-0:1.8.1(08689.832*kWh)
1-0:1.8.2(03163.821*kWh)
1-0:2.8.1(03805.187*kWh)
1-0:2.8.2(09575.965*kWh)
0-0:96.14.0(0001)
1-0:1.7.0(0000.33*kW)
1-0:2.7.0(0000.00*kW)
0-0:96.13.1()
0-0:96.13.0()
0-1:24.1.0(3)
0-1:96.1.0(3238313031353431303034303232323131)
0-1:24.3.0(161005220000)(08)(60)(1)(0-1:24.2.1)(m3)
(04323.740)
!
```

Of met de EMSR 5.0 meter:
```
gej@raspberrypi:~/slimmemeter-rpi $ cu -l /dev/ttyUSB0 -s 115200 --parity=none -E q
Connected.
/Ene5\XS210 ESMR 5.0

1-3:0.2.8(50)
0-0:1.0.0(171104210148W)
0-0:96.1.1(4530303437303030303037363330383137)
1-0:1.8.1(000041.979*kWh)
1-0:1.8.2(000000.000*kWh)
1-0:2.8.1(000017.760*kWh)
1-0:2.8.2(000000.000*kWh)
0-0:96.14.0(0001)
1-0:1.7.0(00.375*kW)
1-0:2.7.0(00.000*kW)
0-0:96.7.21(00003)
0-0:96.7.9(00001)
1-0:99.97.0(0)(0-0:96.7.19)
1-0:32.32.0(00002)
1-0:32.36.0(00000)
0-0:96.13.0()
1-0:32.7.0(232.0*V)
1-0:31.7.0(002*A)
1-0:21.7.0(00.375*kW)
1-0:22.7.0(00.000*kW)
0-1:24.1.0(003)
0-1:96.1.0(4730303538353330303031313633323137)
0-1:24.2.1(171104210000W)(00013.131*m3)
!1A98
```

## Eerst even kijken of we serieel uit kunnen lezen met het script

```

gej@raspberrypi(gej): ~/slimmemeter-rpi $ python P1uitlezen-DSM22.py 
('DSMR P1 uitlezen', '1.1')
Control-C om te stoppen
Pas eventueel de waarde ser.port aan in het python script
5210000)(00)(60)(1)(0-1:24./KMP5 KA6U001660297912

0-0:96.1.1(204B413655303031363630323937393132)
1-0:1.8.1(07041.882*kWh)
1-0:1.8.2(02351.565*kWh)
1-0:2.8.1(03125.397*kWh)
1-0:2.8.2(07729.108*kWh)
0-0:96.14.0(0001)
1-0:1.7.0(0000.54*kW)
1-0:2.7.0(0000.00*kW)
0-0:96.13.1()
0-0:96.13.0()
0-1:24.1.0(3)
0-1:96.1.0(3238313031353431303034303232323131)
0-1:24.3.0(160315210000)(00)(60)(1)(0-1:24.2.1)(m3)
(04083.631)
!
/KMP5 KA6U001660297912

0-0:96.1.1(204B413655303031363630323937393132)
gej@raspberrypi(gej): ~/slimmemeter-rpi $ 
```

Mocht de telegram meer of juist minder dan 20 regels bevatten, dan even aanpassen natuurlijk.
De EMSR 5.0 meter heeft een telegram bericht van 26 regels.

## Daarna kijken of we de telegram kunnen uitlezen en verwerken

```
gej@raspberrypi(gej): ~/slimmemeter-rpi $ python P1uitlezer-DSMR22.py 
('DSMR P1 uitlezer', '1.0')
Control-C om te stoppen
daldag       07041
piekdag      02351
dalterug     03125
piekterug    07729
meter totaal  289  (afgenomen/teruggeleverd van het net vanaf 17-10-2014)
Afgenomen vermogen       2680  W
Teruggeleverd vermogen   0  W
Gas                      4083631  dm3
gej@raspberrypi(gej): ~/slimmemeter-rpi $ 
```

Vooral de nieuwe meters hebben een andere snelheid. Dit kun je aan het begin van het script natuurlijk aanpassen.
Ook de hoeveelheid regels die van een telegram af komen kunnen verschillend zijn. In mijn geval 20 regels.

## Automagiseren met de crontab

```
*/5 * * * *     /root/Script/uitlezen.sh
```

En in het script staat

	# 1 keer per 5 minuten, uitlezen via seriele interface van de slimme meter
	su - gej -c "python /home/gej/P1uitlezer.py > /home/gej/P1uitlezer.txt" 2>&1 >/dev/null
verderop in het script moet je dus die P1uitlezer gebruiken met grep en zo.

## html pagina's
In html staan de pagina's om de scripts via een website uit te lezen (apache, met php)

## fase 2 rrdpower

Als dit allemaal werkt kun je dit in automatisch uitlezen en in de rrd database zetten.
Vervolgens dan nog even de plaatjes genereren, en je hebt een grafische interpretatie van je stroomverbruik.

zie verder in de rrdpower dir.

## Fase 3 mysql

Gebruik van een database voor de opslag van de gegevens.

zie de p1db folder.

