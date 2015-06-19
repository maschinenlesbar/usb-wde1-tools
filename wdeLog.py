#!/usr/bin/python
## # Configuration
databaseFile='/var/lib/usb-wde1/readings.db'
serialPort='/dev/ttyUSB0'
## #
import serial, sys, signal, time, syslog
import sqlite3
from datetime import datetime
syslog.syslog("Starting ...")
# Open serial port
try:
	ser = serial.Serial(serialPort,baudrate=9600,timeout=None)
except serial.SerialException as e:
	syslog.syslog(str(e)+". Exiting.")
	sys.exit(1)
# Catch signals and close serial port gracefully
def signal_handler(signal, frame):
	ser.close()
	db.close()
        sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)
# Setup database connection and database
db = sqlite3.connect(databaseFile)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS measurements(id INTEGER PRIMARY KEY,
		readingTime DATETIME, temp1 REAL, temp2 REAL, temp3 REAL, temp4 REAL,
		temp5 REAL, temp6 REAL, temp7 REAL, temp8 REAL, hum1 REAL,
		hum2 REAL, hum3 REAL, hum4 REAL, hum5 REAL, hum6 REAL, hum7 REAL,
		hum8 REAL, temp9 REAL, hum9 REAL, windspeed REAL,
		rainfall INTEGER, rain BOOLEAN)''')
db.commit()
# Main loop
while True:
	# Wait for data and try error recovery on disconnect
	try:
		serData = ser.readline()
	except serial.SerialException as e:
		try:
			syslog.syslog("Port reports readiness to read but returns no data (disconnected?). Trying repair.")
			ser.close()
			time.sleep(10)
		        ser = serial.Serial(serialPort,baudrate=9600,timeout=None)
			syslog.syslog("Seems the port came back. Continuing.")
			serData = ser.readline()
		except serial.SerialException as f:
		        syslog.syslog(str(f)+". Exiting.")
        		sys.exit(1)
	localTime = datetime.now()
	dataset = serData.split(";")
	# Sanity checks
	if dataset[0] != "$1" or dataset[1] != "1" or (len(dataset[2]) > 0):
		syslog.syslog("Dataset does not conform to ELV OpenFormat specification for USB-WDE1")
	# Parse meter readings into dictionary (abbr. to rd for typing laziness of yours truely)
	rd = {}
	for n in range(1,9):
		# conversion from german decimal mark , to int. .
		rd["temp"+str(n)]=dataset[2+n].replace(",",".")
		rd["hum"+str(n)]=dataset[10+n].replace(",",".")
	# Kombisensor is mapped to temp9/hum9
	rd["temp9"]=dataset[19].replace(",",".")
	rd["hum9"]=dataset[20].replace(",",".")
	rd["windspeed"]=dataset[21]
	rd["rainfall"]=dataset[22]
	rd["rain"]=dataset[23]
	cursor.execute('''INSERT INTO measurements(readingTime,temp1,temp2,temp3,temp4,
			temp5,temp6,temp7,temp8,hum1,hum2,hum3,hum4,hum5,hum6,hum7,hum8,
			temp9,hum9,windspeed,rainfall,rain) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
			(localTime,rd["temp1"],rd["temp2"],rd["temp3"],rd["temp4"],rd["temp5"],
			rd["temp6"],rd["temp7"],rd["temp8"],rd["hum1"],rd["hum2"],rd["hum3"],
			rd["hum4"],rd["hum5"],rd["hum6"],rd["hum7"],rd["hum8"],rd["temp9"],
			rd["hum9"],rd["windspeed"],rd["rainfall"],rd["rain"]))
	db.commit()
