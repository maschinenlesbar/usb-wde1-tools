#!/usr/bin/python
## # Configuration
databaseFile='/var/lib/usb-wde1/readings.db'
## #
import sys, signal, argparse, locale
import sqlite3
from datetime import datetime
# Catch signals and close gracefully
def signal_handler(signal, frame):
	db.close()
        sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)
# Setup getopt and parse arguments
parser = argparse.ArgumentParser(description='Query USB-WDE1 SQLite Database commandline tool.')
group = parser.add_mutually_exclusive_group()
group.add_argument('--temp',action="store",type=int,help='Select temperature reading by sensor number (1-9)')
group.add_argument('--hum',action="store",type=int,help='Select humidity readingy by sensor number (1-9)')
args = parser.parse_args()
# Read args parsed
if args.temp != None:
	wantedColumn="temp"+str(args.temp)
elif args.hum != None:
	wantedColumn="hum"+str(args.hum)
else :
	parser.print_help()
	sys.exit(1)
# Setup database connection and database
db = sqlite3.connect(databaseFile)
cursor = db.cursor()
# Get id of latest measurement
cursor = db.execute('SELECT max(id) FROM measurements')
max_id = cursor.fetchone()[0]
# Get latest measurement
cursor = db.execute("SELECT readingTime,"+wantedColumn+" FROM measurements WHERE id = ?",(str(max_id),))
latest = cursor.fetchone()
print latest[1]
