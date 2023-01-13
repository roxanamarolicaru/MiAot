from MyMQTT import *
import json
import time

class mqttSubscriber():


    def __init__(self,clientID,topic,broker, port):

        self.client=MyMQTT(clientID,broker,port,self)
        self.topic=topic
        self.status=None

    
    def start(self):

        self.client.start()
        self.client.mySubscribe(self.topic)


    def stop(self):

        self.client.stop()


    def notify(self,topic,msg):
        
        #print('notify entry')
        payload=json.loads(msg)
        self.status=payload['e'][0]['v']
        #print(f"payload -> {payload}")
        #print("status=", self.status)