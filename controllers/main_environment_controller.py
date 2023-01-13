import sys
sys.path.append('../utilities')
import Actuator
import Device_threads 
import Sensor 
import client_mqtt as mqtt
import json
import requests
import socket

if __name__ == '__main__':
    
    #Load configuration file
    try:
        conf = json.load(open(str(sys.argv[1])))
    except:
        #No conf provided end script and threads
        print("No configuration file provided as argument")
        sys.exit()
    
    #Get device ip
    my_ip = socket.gethostbyname('localhost')
    print("my ip = ", my_ip)
    
    #Registration to the catalog
    try:
        myjson = {"system_id" : conf["system_id"], 'id': "0", 'name' : conf["bn"]+"_controller", "ip_address" : my_ip,"timestamp" : "0"}
        r = requests.post(conf["miaot_catalog_server_name"], json = myjson)
        r_json = json.loads(r.text)
    except:
        #Catalog unreachable
        print("Problems on reaching the Miaot catalog")
        sys.exit()

    print('----- JSON RESPONSE -----')
    print(r_json)
    
    #Sensor object creation
    sensor1 = Sensor.sensor(id=r_json["assigned_id"], name=conf["sensor"]["name"], unit=conf["sensor"]["unit"])
    actuator1 = Actuator.actuator(id=r_json["assigned_id"], base_name=conf["bn"], name=conf["actuator"]["name"], sensor=sensor1, threshold_min=conf["actuator"]["threshold_min"], threshold_max=conf["actuator"]["threshold_max"])
    
    #Alive_thread started 
    thread_alive = Device_threads.Alive_thread("Alive Thread", conf["system_id"] ,r_json["assigned_id"], conf["miaot_catalog_server_name"] , conf["bn"]+"_controller", my_ip, conf["alive_sleeping_time"])     
    print("Starting thread")
    thread_alive.start() # invokes run method of thread2 
    print("Thread started")

    #Creation of MQTT publisher for the actuator state
    client_id = str(r_json["assigned_id"]) + "_client_actuator"
    topic = str(conf["system_id"])+"/"+conf["bn"]+"/actuator/"
    print("topic = ", topic)
    actuator_mqtt_client = mqtt.DeviceManager(client_id,topic,r_json["message_broker"],r_json["message_broker_port"])
    
    #Creation of MQTT subscriber for sensor measurement 
    client_id = str(r_json["assigned_id"]) + "_client_measurement"
    topic = str(conf["system_id"])+"/"+conf["bn"]+"/"
    print("topic = ", topic)
    measurement_mqtt_client = mqtt.DeviceManager(client_id,topic,r_json["message_broker"],r_json["message_broker_port"])

    print('Actuator clientclient:', actuator_mqtt_client.client)
    actuator_mqtt_client.start()

    print('Measurement client:', measurement_mqtt_client.client)
    measurement_mqtt_client.start()
    
    #Control_thread_actuator started 
    thread_control_actuator = Device_threads.Control_thread_actuator("Control Thread actuator",actuator1, measurement_mqtt_client, actuator_mqtt_client, conf["control_sleeping_time"])
    print("Starting thread")
    thread_control_actuator.start() # invokes run method of thread2 
    print("Thread started")
    


