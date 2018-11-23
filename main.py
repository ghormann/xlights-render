import paho.mqtt.client as paho
import datetime
import json
import time
import ssl
import generate_names as gen

baseNames = ['BRODY', 'EMILY', 'MATT', 'WILL', 'JULIA', 'SOPHIE', 'LONDON', 'MAX', 'BENNY', 'LUIS', 'KORIE']

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
        client.message_callback_add("/christmas/personsName", self.on_name)
        client.message_callback_add("/christmas/currentSong", self.on_song)
        client.username_pw_set(config["username"], config["password"])
        client.connect(host=config["host"], port=config["port"])
        client.loop_start()

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

    # The callback for Names
    def on_name(self, client, userdata, msg):
        name = msg.payload.decode('UTF-8').upper()
        gen.logIt("Received Name " + msg.topic+" "+ name)
        if name in self.namequeue:
            gen.logIt('Name already in queue')
        else:
            gen.logIt('Adding to queue')
            self.namequeue.append(name);

    def updateSong(self):
        gen.logIt("----------------------------")
        gen.logIt(datetime.datetime.now())
        gen.logIt("----------------------------")
        use_me = []
        extra = baseNames.copy()
        while len(use_me) < 10:
            if (len(self.namequeue) > 0):
                use_me.append(self.namequeue.pop(0))
            else:
                use_me.append(extra.pop(0))
        gen.logIt("Genereating with " + str(use_me))
        gen.genereateXml(use_me)
        gen.generateSeq()
        gen.sendSeq()
        gen.logIt("----------------------------")
        gen.logIt(datetime.datetime.now())
        gen.logIt("----------------------------")

        
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    gen.logIt("Connected with result code "+str(rc))
    client.subscribe("/christmas/personsName", 2)
    client.subscribe("/christmas/currentSong", 2)

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("/christmas/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    gen.logIt("Unhandled Topic: " + msg.topic)

if __name__ == "__main__":
    client = MQTTClient()
    client.updateSong()
    while True:
        time.sleep(20) 
    
