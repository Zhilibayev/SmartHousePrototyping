
import RPi.GPIO as GPIO
import serial
import time
import json
import urllib3
import requests
import random
from threading import Thread, Lock
from google.cloud import storage
from picamera import PiCamera
from time import sleep
from serial.tools import list_ports
import os
import urllib2 as ul
import urllib3 as ul3

ul3.disable_warnings(ul3.exceptions.InsecureRequestWarning)
ip = 'https://randomgenerator123.herokuapp.com'
#ip = 'http://10.1.198.17:8080'
port = '/dev/ttyACM0'

for p in list(list_ports.comports()):
	print(p)
	if ('Arduino' in p[1]):
		port = p[0]

credentials_path = '/home/pi/Desktop/firebase/smarthouse-217010-firebase-adminsdk-zoxon-48b4b8fb35.json'
bucket_name = 'smarthouse-217010.appspot.com'
path = '/home/pi/Desktop/serikscode'

writeAPIKeyKitchen = "Y51OU5IL4Y0ANMUX"
writeAPIKeyBedroom = "WB2YAO96388HA9N1"
writeAPIKeyLivingroom = "ID8PBDGIUWOGD250"
channelIdKitchen = "636988"
channelIdBedroom = "638847"
channelIdLivingroom = "639101"

url_kitchen = "https://api.thingspeak.com/channels/" +channelIdKitchen+ "/bulk_update.json"
url_bedroom = "https://api.thingspeak.com/channels/" +channelIdBedroom+ "/bulk_update.json"
url_livingroom = "https://api.thingspeak.com/channels/" +channelIdLivingroom+ "/bulk_update.json"

cloud_inf = {	'kitchen': {'url': url_kitchen, 'api_key': writeAPIKeyKitchen, 'channelID': channelIdKitchen, 'lastConnection': time.time(), 'lastUpdate': time.time(), 'buffer': []},
		'bedroom': {'url': url_bedroom, 'api_key': writeAPIKeyBedroom, 'channelID': channelIdBedroom, 'lastConnection': time.time(), 'lastUpdate': time.time(), 'buffer' : []},
		'common': {'url': url_livingroom, 'api_key': writeAPIKeyLivingroom, 'channelID': channelIdLivingroom, 'lastConnection': time.time(), 'lastUpdate': time.time(), 'buffer': []}}

counter_camera = 0
old = { 'kitchen': 0,
        'common': 0,
        'bedroom': 0}
locker = Lock()
class SendThread(Thread):
    def __init__(self, readings, string_readings):
        Thread.__init__(self)
        self.readings = readings;
	self.readings_str = string_readings

    def httpRequest(self):
	room_name = self.readings["room_name"]
	data = json.dumps({'write_api_key': cloud_inf[room_name]['api_key'], 'updates': cloud_inf[room_name]['buffer']})
	req = ul.Request(url=cloud_inf[room_name]['url'])
	req.add_header("User-Agent","mw.doc.bulk-update")
	req.add_header("Content-Type","application/json")
	req.add_header("Content-Length",str(len(data)))
	req.add_data(data)
	try:
		response = ul.urlopen(req)
		print(response.getcode())
	except ul.HTTPError as e:
		print(e.code)
	cloud_inf[room_name]['buffer'] = []
	cloud_inf[room_name]['lastConnection'] = time.time()

    def updateJson(self):
	room_name = self.readings["room_name"]
	message = {}
	message['delta_t'] = int(round(time.time() - cloud_inf[room_name]['lastUpdate']))
	message['field1'] = self.readings['sensors']['light']
	message['field2'] = self.readings['sensors']['pir']
	cloud_inf[room_name]['buffer'].append(message)
	if time.time() - cloud_inf[room_name]['lastConnection'] >= postingInterval:
		self.httpRequest()

    def run(self):
	room_name = self.readings["room_name"]
	if time.time() - cloud_inf[room_name]['lastUpdate'] >= updateInterval:
		locker.acquire()
		self.updateJson()
		locker.release()
	http = urllib3.PoolManager()
        time.sleep(0.1)

        sensorValue = self.readings_str.decode('utf-8')
        http.request('POST', ip + '/query',
        	body = sensorValue,
        	headers = {'Content-Type': 'application/json'})

class GetThread(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		http = urllib3.PoolManager()
		r = http.request('GET', ip+'/test/3')
		x = json.loads(str(r.data))
    		#y = "1:1,1;2:0,0;3:1,0;"
		y = "1:"  + str(x['kitchen']['ss']) + "," + str(x['kitchen']['ls']) + ";2:" + str(x['bedroom']['ss']) + "," + str(x['bedroom']['ls']) + ";3:" + str(x['common']['ss']) + "," + str(x['common']['ls']) + ";*"
		print(y)
		ArduinoSerial.write(y.encode())

mutex = Lock()

class ServoThread(Thread):

	def __init__(self, room_name, value, gpio, p, servopin, angle):
                Thread.__init__(self)
		self.room_name = room_name
		self.value = value
		self.gpio = gpio
		self.p = p
		self.servopin = servopin
		self.angle = angle
		#self.bucket = bucket
		#self.camera = camera

	def run(self):
		mutex.acquire()
		global counter_camera
       		duty = self.angle/18 + 2
                self.gpio.output(self.servopin, True)
                self.p.ChangeDutyCycle(duty)
                time.sleep(0.5)
                self.gpio.output(self.servopin, False)
                self.p.ChangeDutyCycle(0)
		#new_name = self.room_name +".jpeg"
		#blob = self.bucket.blob(new_name)
        	#self.camera.capture(new_name)
        	#blob.upload_from_filename(new_name)
		#counter_camera += 1
		mutex.release()

def check_rotate(room_name, value, gpio, p, servopin):
		x["kitchen"] = 0
		x["livingroom"] = 180
		x["bedroom"] = 90

		if (value > 650 and old[room_name] < 650):
				print(room_name)
				#ServoThread(room_name, value, gpio, p, servopin, x[room_name]).start()
                		duty = x[room_name]/18 + 2
                		gpio.output(servopin, True)
                		p.ChangeDutyCycle(duty)
                		time.sleep(1)
                		gpio.output(servopin, False)
                		p.ChangeDutyCycle(0)
		old[room_name] = value

#print("Setting GPIO and Servomotor")
#servoPIN = 17
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(servoPIN, GPIO.OUT)
#p = GPIO.PWM(servoPIN, 50)
#p.start(0)

print("Setting Ardiono Connection")
ArduinoSerial = serial.Serial() #'Com3' #"/dev/cu.usbmodemFD121"#Create Serial port object called arduinoSerialData
ArduinoSerial.port = port
ArduinoSerial.baudrate = 115200
ArduinoSerial.timeout = 1
ArduinoSerial.setDTR(False)
ArduinoSerial.open()
time.sleep(2)
 
#print("Setting HTTP Connection")
#http = urllib3.PoolManager()

#print("Setting Camera")
#camera = PiCamera()
#camera.resolution = (256, 256)

#print("Setting Google Storage")
#storage_client = storage.Client().from_service_account_json(credentials_path)
#bucket = storage_client.get_bucket(bucket_name)

print("Setting ThingSpeak")
postingInterval = 30
updateInterval = 5

counter = 0

millis1 = int(round(time.time()*1000))
try:
	while 1:
		time.sleep(1)

		while ArduinoSerial.in_waiting:
			sensorReading = ArduinoSerial.readline()
			try:
				#print(sensorReading)
				#print("Hello")
				x = json.loads(sensorReading)
				#SendThread(x, sensorReading).start()
				#check_rotate(str(x['room_name']), int(x['sensors']['pir']), GPIO, p, servoPIN)
			except ValueError:
			        print("Corruption VALUE!!")
			except KeyError:
			        print("Corruption KEY!!")
			current = int(round(time.time()*1000))
			if ( current-millis1 > 500):
				GetThread().start()
				millis1 = current

except KeyboardInterrupt:
	print("Hello")
	#p.stop()
	#GPIO.cleanup()
