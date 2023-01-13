import cherrypy
import json
import datetime
from MyMQTT import *
import time

class DeviceManager:


    def __init__(self, clientID, topic,broker,port):

        self.topic = topic
        self.client = MyMQTT(clientID,broker,port,None)
        self.statusToBool = {"on":1,"off":0}


    def start (self):

        print("to start")
        self.client.start()
        print("started")


    def stop (self):

        self.client.stop()


    def publish(self, message):

        #print("to publish")
        self.client.myPublish(self.topic,message)
        #print("published")




if __name__ == "__main__":
    
    conf=json.load(open("settings_mosquitto.json"))
    broker=conf["broker"]
    port=conf["port"]
    deviceManager = DeviceManager("LedCommander","raspberry_collar/",broker,port)
    
    print('client:', deviceManager.client)
    deviceManager.start()

    print('Welcome to the client to switch on/off the lamp\n')
    done=False
    command_list='Type:\n"on" to set the light on\n"off" to set it off\n"q" to quit\n'
    while not done:
        print(command_list)
        user_input=input()
        if user_input!='q':
            deviceManager.publish({'e':[{'v':user_input}]})
        elif user_input=='q':
            done=True
        else:
            print('Unknown command')
            
    deviceManager.client.stop()   
