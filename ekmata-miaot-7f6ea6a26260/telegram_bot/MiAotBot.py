import json
import time
import requests
import sys
sys.path.append('../utilities')
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from urllib import request
import logging
from MyMQTT import *
import mqtt_subscriber as mqtt_sub
from PIL import Image
import imgkitTS as img


class MiAotBot:

    exposed=True

    def __init__(self,token,broker,port,topic,devices):

        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs=[]
        self.chat_states=[]
        self.topic = topic
        self.devices = devices
        self.client = mqtt_sub.mqttSubscriber("telegramBotIoT",topic, broker, port)
        self.client.start()
        self.__message={"alert":"","action":""}

        MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()


    #function triggered when message is sent to the bot 
    def on_chat_message(self, msg):

        content_type, chat_type, chat_ID = telepot.glance(msg)
        
        print(type(chat_ID))
        message = msg['text']
        chat_state = next((x for x in self.chat_states if x["id"]==chat_ID),None)
        if chat_state == None:
             
             chat_state = {"id":chat_ID,"state":0,"system_id":-1}
             self.chat_states.append(chat_state)
             
        if chat_state["state"]==0:
            catalog_r = requests.get(conf["catalog_address"],params={"system_id":message})
            catalog_r_json = json.loads(catalog_r.text)
            if catalog_r_json["assigned_id"]==-1:   
                if chat_ID not in self.chatIDs:
                    self.bot.sendMessage(chat_ID, text="Welcome to MiAot Bot! Please send your system ID:")
                else:
                    self.bot.sendMessage(chat_ID, text="This system ID does not exist, please try again.")
                self.chatIDs.append(chat_ID)
                return
            else:
                chat_state["state"] = 1
                chat_state["system_id"] = message
                self.bot.sendMessage(chat_ID, text="Welcome system ID "+message+"!")

                return

        if message=="/ismycatathome":

            response=self.collarSearch()
            self.bot.sendMessage(chat_ID, text=response)

        elif(message=="/miao"):

            #Easter egg, sends a meme from Reddit (link specified in configuration file)
            self.bot.sendPhoto(chat_ID, conf["easter_egg"])

        elif(message == "/showdevices"):
            
            self.keyboard_on_chat_message(message,chat_ID)

        else:

            self.bot.sendMessage(chat_ID, text="Command not supported") 
        

    def keyboard_on_chat_message(self,msg,chat_ID):
        
        d_obj = devices
        kbs=[]
        index=0

        #Dinamically populate the menu with the user devices.
        for x in d_obj:
            index = index + 1
            kbs = kbs + [InlineKeyboardButton(text=x, callback_data=index)]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [x] for x in kbs
        ])

        self.bot.sendMessage(chat_ID, 'These are your devices. Tap to see the statistics.', reply_markup=keyboard)


    def on_callback_query(self,msg):
        
        #Read the answer when the user taps one of the inline keyboard button.
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)

        self.bot.sendMessage(from_id, text='This is the plot about your '+self.devices[int(query_data)-1]+'.')
        img.retrievePlot(from_id,query_data)
        self.bot.sendPhoto(from_id, open('./'+str(from_id)+'_'+query_data+'_'+'tmp.jpg','rb'))

    
    def collarSearch(self):
        
        #Read the status of the collar.
        message=self.client.status
        n=""

        if message == True:
            response="Yes"

        else:
            response="No"
            n=" not"

        return response + ", your cat is" + n +" at home."


if __name__ == "__main__":
    
    #Load configuration file
    try:
        conf = json.load(open(str(sys.argv[1])))
    except:
        #No conf provided end script and threads
        print("No configuration file provided as argument")
        sys.exit()

    #Read token from configuration file
    token = conf["token"]

    #Contact the catalog to retrieve broker and port
    catalog_r = requests.get(conf["catalog_address"])
    print(catalog_r.text)
    catalog_r_json = json.loads(catalog_r.text)
    broker = catalog_r_json["message_broker"]
    port = catalog_r_json["message_broker_port"] 
    topic=conf["topic"]
    
    #Find the devices used by thingspeak
    try:
        thingspeak_conf=json.load(open(conf["thingspeak_settings"]))
        devices=thingspeak_conf["bn"]
    except:
        #No conf provided end script and threads
        print("No thingspeak configuration file location provided in telegram settings file")
        sys.exit()

    sb=MiAotBot(token,broker,port,topic,devices)
    
    while 1: 
        print("Listening...")
        time.sleep(10)
