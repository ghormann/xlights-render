import paho.mqtt.client as paho
import datetime
import json
import time
import ssl
from random import shuffle
import generate_names as gen
from config import GregLightsConfig

epoch = datetime.datetime.utcfromtimestamp(0)


def unix_ts(dt):
	return (dt - epoch).total_seconds()


def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code"""
	if isinstance(obj, (datetime.datetime, datetime.date)):
		return obj.isoformat()
	raise TypeError("Type %s not serializable" % type(obj))


class MQTTClient:
	"""Very simple MQTTClient for listening to names to be displayed on Grid"""
	def __init__(self, config: GregLightsConfig):
		self.config = config
		client = paho.Client(paho.CallbackAPIVersion.VERSION1)
		self.client = client
		#client.tls_set(ca_certs=config.ca_file, tls_version=ssl.PROTOCOL_TLSv1_2)
		client.on_connect = self._on_connect
		client.on_message = self._on_message
		self.status = "IDLE"
		self.birthday = ""
		self.namequeue = []
		self.namequeue_low = []
		self.namequeue_ready = []
		self.midnight_names = []
		client.message_callback_add("/christmas/personsName", self.on_name)
		client.message_callback_add("/christmas/personsNameFront", self.on_name_front)
		client.message_callback_add("/christmas/personsNameRemove", self.on_name_remove)
		client.message_callback_add("/christmas/personsNameLow", self.on_name_low)
		client.message_callback_add("/christmas/nameAction", self.on_action)
		client.message_callback_add("/christmas/nameBirthday", self.on_birthday)
		client.username_pw_set(config.username, config.password)
		client.connect(host=config.host, port=config.port)
		client.loop_start()

	def _on_connect(self, client, userdata, flags, rc):
		gen.logIt("Connected with result code " + str(rc))
		client.subscribe("/christmas/personsName", 2)
		client.subscribe("/christmas/personsNameFront", 2)
		client.subscribe("/christmas/personsNameRemove", 2)
		client.subscribe("/christmas/personsNameLow", 2)
		client.subscribe("/christmas/nameAction", 2)
		client.subscribe("/christmas/nameBirthday", 2)
		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.

	def _on_message(self, client, userdata, msg):
		gen.logIt("Unhandled Topic: " + msg.topic)

	def publishQueue(self):
		full_queue = {}
		full_queue["ready"] = self.namequeue_ready
		full_queue["low"] = self.namequeue_low
		full_queue["normal"] = self.namequeue
		full_queue["status"] = self.status
		json_data = json.dumps(full_queue, default=json_serial)
		self.client.publish("/christmas/nameQueue", json_data)

	def insert_midnight_name(self, name):
		if name in self.midnight_names:
			gen.logIt('Name already in midnight queue')
		else:
			self.midnight_names.insert(0, name)
		if len(self.midnight_names) > 150:
			del self.midnight_names[150:]

	def on_birthday(self, client, userdata, msg):
		name = msg.payload.decode('UTF-8').upper()
		gen.logIt("Received Birthday " + msg.topic + " " + name)
		self.birthday = name

	def on_action(self, client, userdata, msg):
		action = msg.payload.decode('UTF-8').upper()
		gen.logIt("Received Action " + msg.topic + " " + action)
		if "GENERATE_MIDNIGHT" == action:
			self.status = "PENDING_MIDNIGHT"
		elif "GENERATE" == action and "IDLE" == self.status:
			self.status = "PENDING"
		elif "RESET" == action and "READY_MIDNIGHT" == self.status:
			self.status = "IDLE"
		elif "RESET" == action and "READY" == self.status:
			self.status = "IDLE"
			self.namequeue_ready = []
		else:
			gen.logIt("ERROR: Invalid action " + msg.topic + " " + action + " while in state " + self.status)

	def on_name_front(self, client, userdata, msg):
		data = json.loads(msg.payload.decode('UTF-8'))
		gen.logIt("Received Name for Front " + msg.topic + " " + data['name'])
		self.namequeue.insert(0, data)
		self.insert_midnight_name(data['name'])

	def on_name_remove(self, client, userdata, msg):
		data = json.loads(msg.payload.decode('UTF-8'))
		name = data['name']
		gen.logIt("Received Name for Remove " + msg.topic + " " + name)
		for i, obj in enumerate(self.namequeue):
			if obj['name'] == name:
				del self.namequeue[i]
				break
		for i, obj in enumerate(self.namequeue_low):
			if obj['name'] == name:
				del self.namequeue_low[i]
				break

	def on_name(self, client, userdata, msg):
		data = json.loads(msg.payload.decode('UTF-8'))
		name = data['name']
		self.insert_midnight_name(name)
		gen.logIt("Received Name " + msg.topic + " " + name)
		found = False
		for obj in self.namequeue:
			if obj['name'] == name:
				found = True
				break
		if found:
			gen.logIt('Name already in queue')
		else:
			self.namequeue.append(data)
			gen.logIt('Adding to queue, size: ' + str(len(self.namequeue)))

	def on_name_low(self, client, userdata, msg):
		data = json.loads(msg.payload.decode('UTF-8'))
		name = data['name']
		self.insert_midnight_name(name)
		gen.logIt("Received Name " + msg.topic + " " + name)
		found = False
		for obj in self.namequeue_low:
			if obj['name'] == name:
				found = True
				break
		if found:
			gen.logIt('Name already in queue')
		else:
			self.namequeue_low.append(data)
			gen.logIt('Adding to queue, size: ' + str(len(self.namequeue_low)))

	def getBirthday(self):
		return self.birthday

	def getStatus(self):
		return self.status

	def genBirthday(self):
		gen.generateBirthday(self.birthday, self.config.fpp_ips)
		self.birthday = ""

	def updateSong(self, midnight=False):
		gen.logIt("----------------------------")
		gen.logIt(datetime.datetime.now())
		gen.logIt('Queue size: ' + str(len(self.namequeue)))
		gen.logIt('Queue size Low: ' + str(len(self.namequeue_low)))
		gen.logIt("----------------------------")

		self.status = "GENERATING"
		if midnight:
			self.status = "GENERATING_MIDNIGHT"
		self.publishQueue()
		time.sleep(1)
		if midnight:
			self.midnight_names.sort()
			midnight_str = " ".join(self.midnight_names)
			gen.genereateMidnightXml(midnight_str)
		else:
			use_me = []
			use_me_names = []
			extra = self.config.base_names.copy()
			shuffle(extra)
			while len(use_me) < 13:
				if len(self.namequeue) > 0:
					obj = self.namequeue.pop(0)
					use_me.append(obj)
					use_me_names.append(obj['name'])
				elif len(self.namequeue_low) > 0:
					obj = self.namequeue_low.pop(0)
					use_me.append(obj)
					use_me_names.append(obj['name'])
				else:
					obj = {}
					obj['name'] = extra.pop(0)
					obj['ts'] = unix_ts(datetime.datetime.utcnow())
					obj['from'] = 'System'
					use_me.append(obj)
					use_me_names.append(obj['name'])
			gen.logIt("Genereating with " + str(use_me_names))
			self.namequeue_ready = use_me.copy()
			gen.genereateXml(use_me_names)
		gen.generateSeq(midnight)
		gen.sendSeq(midnight, self.config.fpp_ips)
		# Done
		self.status = "READY"
		if midnight:
			self.status = "READY_MIDNIGHT"
		gen.logIt("----------------------------")
		gen.logIt(datetime.datetime.now())
		gen.logIt("----------------------------")


if __name__ == "__main__":
	client = MQTTClient(GregLightsConfig())
	#client.updateSong()
	while True:
		time.sleep(2)
		if "PENDING" == client.getStatus():
			client.updateSong()
		if "PENDING_MIDNIGHT" == client.getStatus():
			client.updateSong(True)
		if "" != client.getBirthday():
			client.genBirthday()

		client.publishQueue()
