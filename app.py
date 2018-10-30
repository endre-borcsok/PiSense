from flask import Flask
import sys
import os
import socket
import Adafruit_DHT

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
	    return 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity)
	else:
	    print('Failed to get reading. Try again!')
	    return ''

@app.route("/")
def hello():
	reading = readSensor()
	print reading
	html = '<h3>' + reading + '!</h3>' + '<b>Hostname:</b> {hostname}<br/>'
	return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=0)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)