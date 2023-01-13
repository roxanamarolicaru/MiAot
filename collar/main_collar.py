import Collar_thread as ct
import json
import sys
sys.path.append('../utilities')
import client_mqtt as mqtt
import requests
import socket
import time



if __name__ == "__main__":

    #Get device ip
    my_ip = socket.gethostbyname('localhost')
    print("my ip = ", my_ip)

    #Load configuration file
    try:
        conf = json.load(open(str(sys.argv[1])))
    except:
        #No conf provided end script and threads
        print("No configuration file provided as argument")
        sys.exit()
    
    #Connect and register to miaot catalog
    try:
        myjson = {"system_id" : conf["system_id"], 'id': "0", 'name' : conf["bn"], "ip_address" : my_ip,"timestamp" : "0"}
        r = requests.post(conf["miaot_catalog_server_name"], json = myjson)
        r_json = json.loads(r.text)
        client_id = r_json["assigned_id"]
        topic = str(conf["system_id"])+ "/"+conf["bn"]+"/"
    except:
        #Catalog unreachable
        print("Problems on reaching the Miaot catalog")
        sys.exit()

    print("client_id = ", client_id)
    print("topic = ", topic)
    print("broker = ", r_json["message_broker"])
    print("port = ", r_json["message_broker_port"])
    
    deviceManager = mqtt.DeviceManager(str(client_id),topic,r_json["message_broker"],r_json["message_broker_port"])
    deviceManager.start()
    
    print('ip_to_ping = ', conf["IP_to_ping"])


    #Pinging_thread started 
    pinging_thread = ct.Pinging_thread("Control Thread",conf["IP_to_ping"], deviceManager, conf["bn"], conf["control_sleeping_time"])     
    print("Starting thread")
    pinging_thread.start() # invokes run method of thread2 
    print("Thread started")


    #Alive_thread started 
    thread_alive_collar = ct.Alive_thread_collar("Alive Thread collar", conf["system_id"],r_json["assigned_id"], conf["miaot_catalog_server_name"] , conf["bn"], my_ip, conf["alive_sleeping_time"])     
    print("Starting thread")
    thread_alive_collar.start() # invokes run method of thread2 
    print("Thread started")

    