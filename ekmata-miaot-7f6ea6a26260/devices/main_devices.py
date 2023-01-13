import sys
sys.path.append('../utilities')
import Actuator
import Device_threads 
import Sensor 
import Simulator 
import client_mqtt as mqtt
import json
import requests
import socket

SIMULATED = True

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
        myjson = {"system_id" : conf["system_id"], 'id': "0", 'name' : conf["bn"], "ip_address" : my_ip,"timestamp" : "0"}
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

    if (SIMULATED):
        # ================ SIMULATION OF DEVICE ================

        simulator1=Simulator.simulator(conf["simulator"]["initial_condition"],conf["simulator"]["loading_rate"],conf["simulator"]["downloading_rate"],conf["simulator"]["sleeping_time"])
        
        # =======================================================
    
    
    #Alive_thread started 
    thread_alive = Device_threads.Alive_thread("Alive Thread", conf["system_id"],r_json["assigned_id"], conf["miaot_catalog_server_name"] , conf["bn"], my_ip, conf["alive_sleeping_time"])     
    print("Starting thread")
    thread_alive.start() # invokes run method of thread2 
    print("Thread started")
    
    #Creation of MQTT publisher for the sensor measurements
    client_id = r_json["assigned_id"]
    topic = str(conf["system_id"])+"/"+ conf["bn"]+"/"
    print("client_id = ", client_id)
    print("topic = ", topic)
    deviceManager = mqtt.DeviceManager(str(client_id),topic,r_json["message_broker"],r_json["message_broker_port"])
    
    #Creation of MQTT publisher for the actuator state
    client_id = str(r_json["assigned_id"]) + "_client"
    topic = str(conf["system_id"])+"/"+ conf["bn"]+"/actuator/"
    print("topic = ", topic)
    actuator_mqtt_client = mqtt.DeviceManager(client_id,topic,r_json["message_broker"],r_json["message_broker_port"])
    
    print('client:', deviceManager.client)
    deviceManager.start()
    
    print('client:', actuator_mqtt_client.client)
    actuator_mqtt_client.start()
    
    #Control_thread started 
    thread_control = Device_threads.Control_thread("Control Thread",actuator1, deviceManager, actuator_mqtt_client, conf["control_sleeping_time"])
    print("Starting thread")
    thread_control.start() # invokes run method of thread2 
    print("Thread started")

    if (SIMULATED):
        # ================ SIMULATION OF DEVICE ================

        #Simulator_thread started 
        thread_simulator = Device_threads.Simulator_thread("Simulator Thread",actuator1, simulator1)     
        print("Starting thread")
        thread_simulator.start() # invokes run method of thread2 
        print("Thread started")

        # ======================================================
    else:
        print("REAL DEVICE")
        # ==================== REAL DEVICE =====================
        #
        # A creation of a new thread is needed in order to manage real 
        # measurements and actuators updating frequently the measure 
        # through the following functions:
        #
        #   >> actuator1.sensor.read_measure( <measure_from_sensor> )
        #   >> if (actuator1.state):
        #   >>      #Turn on actuator
        #   >>      <Function_to_turn_on_actuator()>
        #   >> else:    
        #   >>      #Turn off actuator
        #   >>      <Function_to_turn_off_actuator()>
        #
        # ========================================================
