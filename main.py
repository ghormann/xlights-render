import paho.mqtt.client as paho
import datetime
import json
import time
import ssl
from random import shuffle
import generate_names as gen

baseNames = ['JEFF', 'BRADY','MARY', 'NANCY','JERRY', 'HENERY', 'ALEX', 'TIM', 'ABBIE','MELISSA', 'JUDY', 'BRODY', 'EMILY', 'MATT', 'WILL', 'JULIA', 'SOPHIE', 'LONDON', 'MAX', 'BENNY', 'LUIS', 'KORIE']

class MQTTClient:
    """Very simple MQTTClient for listening to names to be displayed on Grid"""
    def __init__(self):
        config = json.load(open('greglights_config.json'))
        client = paho.Client()
        self.client = client
        client.tls_set(ca_certs=config["ca_file"], tls_version=ssl.PROTOCOL_TLSv1_2)
        client.on_connect = on_connect
        client.on_message = on_message
        self.namequeue = []
        self.namequeue_low = []
        client.message_callback_add("/christmas/personsName", self.on_name)
        client.message_callback_add("/christmas/personsNameFront", self.on_name_front)
        client.message_callback_add("/christmas/personsNameRemove", self.on_name_remove)
        client.message_callback_add("/christmas/personsNameLow", self.on_name_low)
        client.message_callback_add("/christmas/currentSong", self.on_song)
        client.username_pw_set(config["username"], config["password"])
        client.connect(host=config["host"], port=config["port"])
        client.loop_start()

    def publishQueue(self):
        json_data = json.dumps(self.namequeue)
        self.client.publish("/christmas/nameQueue", json_data)

        json_data = json.dumps(self.namequeue_low)
        self.client.publish("/christmas/nameQueueLow", json_data)

    # The callback for Song 
    def on_song(self, client, userdata, msg):
        song = msg.payload.decode('UTF-8').upper()
        gen.logIt("Received SOng " + msg.topic+" "+ song)
        if "SUGAR_PLUM" in song:
            self.updateSong()
        if "HERECOMES" in song:
            self.updateSong()
        if "LITTLEDRUMMER" in song:
            self.updateSong()
        if "HOUSEONC" in song:
            self.updateSong()

    def on_name_front(self, client, userdata, msg):
        name = msg.payload.decode('UTF-8').upper()
        gen.logIt("Received Name for Front " + msg.topic+" "+ name)
        self.namequeue.insert(0,name)
        self.publishQueue()

    def on_name_remove(self, client, userdata, msg):
        name = msg.payload.decode('UTF-8').upper()
        gen.logIt("Received Name for Remove " + msg.topic+" "+ name)
        while name in self.namequeue:
            self.namequeue.remove(name)
        while name in self.namequeue_low:
            self.namequeue_low.remove(name)
        self.publishQueue()

    # The callback for Names
    def on_name(self, client, userdata, msg):
        name = msg.payload.decode('UTF-8').upper()
        gen.logIt("Received Name " + msg.topic+" "+ name)
        if name in self.namequeue:
            gen.logIt('Name already in queue')
        else:
            self.namequeue.append(name);
            gen.logIt('Adding to queue, size: ' + str(len(self.namequeue)))
        self.publishQueue() 

    # The callback for Names Low Priority
    def on_name_low(self, client, userdata, msg):
        name = msg.payload.decode('UTF-8').upper()
        gen.logIt("Received Low Priroity Name " + msg.topic+" "+ name)
        if name in self.namequeue_low:
            gen.logIt('Name already in Low queue')
        else:
            self.namequeue_low.append(name);
            gen.logIt('Adding to Low queue, size: ' + str(len(self.namequeue)))
        self.publishQueue() 

    def updateSong(self):
        gen.logIt("----------------------------")
        gen.logIt(datetime.datetime.now())
        gen.logIt('Queue size: ' + str(len(self.namequeue)))
        gen.logIt('Queue size Low: ' + str(len(self.namequeue_low)))
        gen.logIt("----------------------------")
        use_me = []
        extra = baseNames.copy()
        shuffle(extra)
        while len(use_me) < 13:
            if (len(self.namequeue) > 0):
                use_me.append(self.namequeue.pop(0))
            elif (len(self.namequeue_low) > 0):
                use_me.append(self.namequeue_low.pop(0))
            else:
                use_me.append(extra.pop(0))
        gen.logIt("Genereating with " + str(use_me))
        gen.genereateXml(use_me)
        gen.generateSeq()
        gen.sendSeq()
        self.publishQueue() 
        gen.logIt("----------------------------")
        gen.logIt(datetime.datetime.now())
        gen.logIt("----------------------------")

        
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    gen.logIt("Connected with result code "+str(rc))
    client.subscribe("/christmas/personsName", 2)
    client.subscribe("/christmas/personsNameFront", 2)
    client.subscribe("/christmas/personsNameRemove", 2)
    client.subscribe("/christmas/personsNameLow", 2)
    client.subscribe("/christmas/currentSong", 2)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("/christmas/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    gen.logIt("Unhandled Topic: " + msg.topic)

if __name__ == "__main__":
    client = MQTTClient()
    #client.updateSong()
    while True:
        time.sleep(20) 
        client.publishQueue()
    
