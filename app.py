from flask import Flask
import sys
import os
import socket
import time
import threading
from threading import Thread
import Adafruit_DHT
import MySQLdb

db = MySQLdb.connect("localhost", "monitor", "password", "temps")
curs = db.cursor()
app = Flask(__name__)

sensor_args = { '11': Adafruit_DHT.DHT11,
		        '22': Adafruit_DHT.DHT22,
		        '2302': Adafruit_DHT.AM2302 }

if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
	sensor = sensor_args[sys.argv[1]]
	pin = sys.argv[2]
else:
    print('Usage: sudo ./app.py [11|22|2302] <GPIO pin number>')
    print('Example: sudo ./app.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')

def readSensor():
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	if humidity is not None and temperature is not None:
		addTempToDb('living-room', temperature, humidity)
		return getRecentTempData()
	else:
	    return 'Failed to get reading. Try again!'

def addTempToDb(location, temp, humidity):
	 curs.execute ("INSERT INTO tempdat values(CURRENT_DATE() - INTERVAL 1 DAY, NOW(), %s, %s, %s)", (location, temp, humidity))
	 db.commit()

def runTemperatureMonitor():
	print(time.ctime())
	print(readSensor())
	threading.Timer(30, runTemperatureMonitor).start()

def getRecentTempData():
	curs.execute("SELECT * FROM tempdat LIMIT 1")
	data = curs.fetchall()
	return "Temperature: %s C, Humidity: %s %%" % (data[0][3], data[0][4])

@app.route("/")
def hello():
	reading = getRecentTempData()
	print reading
	html = '<h3>' + reading + '</h3>' + '<b>Hostname:</b> {hostname}<br/>'
	return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=0)

if __name__ == "__main__":
	thread = Thread(target = runTemperatureMonitor)
	thread.start()
	thread.join()
	app.run(host='0.0.0.0', port=80)