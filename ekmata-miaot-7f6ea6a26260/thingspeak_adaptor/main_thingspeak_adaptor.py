import sys
sys.path.append('../utilities')
import mqtt_subscriber as mqtt_subs 
import MyMQTT
import json
import requests
import socket
import time

if __name__ == '__main__':
      
    #Load conf file
    try:
        conf = json.load(open(str(sys.argv[1])))
    except:
        #No conf provided end script and threads
        print("No configuration file provided as argument")
        sys.exit()

    #Get device ip
    my_ip = socket.gethostbyname('localhost')
    print("my ip = ", my_ip)

    #Get device list from the catalog
    try:
        catalog_r = requests.get(conf["catalog_address"])
        catalog_r_json = json.loads(catalog_r.text)
    except:
        #Catalog unreachable
        print("Problems on reaching the Miaot catalog")
        sys.exit()

    # For each device subscribe to its corrispondent topic
    bn_list=[]
    
    for bn in conf["bn"]: 

        topic= str(conf["system_id"])+"/"+bn+"/"
        mydevice=mqtt_subs.mqttSubscriber(str(conf["system_id"])+bn, str(topic) ,catalog_r_json["message_broker"], catalog_r_json["message_broker_port"])
        mydevice.start()
        bn_list.append(mydevice)
    
    while True:

        #JSON to be send to the thingspeak
        myjson=conf["thingspeak_key"]
        
        #Update for the device list information to be delivered to Thingspeak
        for i in range(len(bn_list)):

            #Key for the Thingspeak JSON
            pos="field"+str(i+1)
            #Value for the Thingspeak JSON
            myjson[pos]=bn_list[i].status
        
        #Update channels information through REST request
        r = requests.post("https://api.thingspeak.com/update.json", json = myjson)
        r_json = json.loads(r.text)
        print('----- JSON RESPONSE -----')
        print(r_json)
        
        #Sleep for a time
        time.sleep(conf["adaptor_sleeping_period"])
    

