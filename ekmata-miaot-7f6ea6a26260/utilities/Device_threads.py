import threading 
import requests
import time 
from datetime import datetime
from MyMQTT import *

class Alive_thread( threading.Thread ):


    def __init__(self, threadName, System_id, index, miaot_catalog, base_name, my_ip, sleepTime=5):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.index=index
        self.system_id=System_id
        self.sleepTime = sleepTime
        self.miaot_catalog=miaot_catalog
        self.base_name = base_name
        self.my_ip = my_ip

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)
                

    # overridden Thread run method
    def run( self ):

        while(True):
            
            new_json = {"system_id" : self.system_id, 'id': self.index, 'name' : self.base_name, "ip_address" : self.my_ip,"timestamp" : "0"}
            requests.put(self.miaot_catalog, json = new_json)

            #print('----- NEW_JSON RESPOSE -----')
            #print(new_json)
            
            #print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            #print(str(self.getName()), "done sleeping")
            
   


class Control_thread( threading.Thread): 


    def __init__(self, threadName, actuator, deviceManager, actuator_mqtt_client, sleepTime=5):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.actuator=actuator
        self.deviceManager=deviceManager
        self.actuator_mqtt_client=actuator_mqtt_client

        #EDIT: notify modified 
        self.actuator_mqtt_client.client.paho_mqtt.on_message=self.notify1

        self.actuator_mqtt_client.client.mySubscribe(self.actuator_mqtt_client.topic)

        self.sleepTime = sleepTime
        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    def notify1(self, paho_mqtt , userdata, msg):

        #Read update from MQTT broker
        payload=json.loads(msg.payload)
        self.actuator.state = payload['e'][0]['vb']
        

    def notify(self,topic,msg):

        #Read update from MQTT broker
        payload=json.loads(msg)
        self.actuator.state = payload['e'][0]['vb']
                

    # overridden Thread run method
    def run( self ):

        while(True):
            
            self.actuator.run_control(self.actuator_mqtt_client)
            self.deviceManager.publish(self.actuator.to_message_sensor())
            #print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            #print(str(self.getName()), "done sleeping")
            



class Control_thread_actuator( threading.Thread):


    def __init__(self, threadName, actuator, measurement_mqtt_client, actuator_mqtt_client, sleepTime=5):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.actuator=actuator
        self.measurement_mqtt_client=measurement_mqtt_client
        self.actuator_mqtt_client=actuator_mqtt_client
        self.sleepTime = sleepTime

        #EDIT: notify modified 
        self.actuator_mqtt_client.client.paho_mqtt.on_message=self.notify1
        self.measurement_mqtt_client.client.paho_mqtt.on_message=self.notify2

        self.actuator_mqtt_client.client.mySubscribe(self.actuator_mqtt_client.topic)
        self.measurement_mqtt_client.client.mySubscribe(self.measurement_mqtt_client.topic)

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    #notify actuator 
    def notify1 (self, paho_mqtt , userdata, msg):

        #Read update from MQTT broker
        payload=json.loads(msg.payload)
        self.actuator.state = payload['e'][0]['vb']
        #print(">>>>>>>>>> actuator ",payload)
    

    #notify sensor
    def notify2 (self, paho_mqtt , userdata, msg):

        #Read update from MQTT broker
        payload=json.loads(msg.payload)
        self.actuator.sensor.measure = payload['e'][0]['v']
        #print(">>>>>>>>>> sensor ",payload)
        
                
    # overridden Thread run method
    def run( self ):

        while(True):
            
            self.actuator.run_control(self.actuator_mqtt_client)
            #print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            #print(str(self.getName()), "done sleeping")
        



class Simulator_thread( threading.Thread): 


    def __init__(self, threadName, actuator, simulator):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.actuator=actuator
        self.simulator=simulator
        self.sleepTime = self.simulator.delta_t

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    # overridden Thread run method
    def run( self ):

        while(True):
            
            self.simulator.run(self.actuator.state)
            self.actuator.sensor.read_measure(self.simulator.actual_state)

            print(f"simulator.actual_state -> {self.simulator.actual_state}")
            #print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            
            time.sleep( self.sleepTime )
            #print(str(self.getName()), "done sleeping")




class Control_thread_timer( threading.Thread):


    def __init__(self, threadName, actuator, actuator_mqtt_client_timer, timestamp_list, sleepTime=5):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.actuator=actuator
        self.actuator_mqtt_client_timer=actuator_mqtt_client_timer
        self.sleepTime = sleepTime
        self.timestamp_list = timestamp_list

        #EDIT: notify modified 
        self.actuator_mqtt_client_timer.client.paho_mqtt.on_message=self.notify

        self.actuator_mqtt_client_timer.client.mySubscribe(self.actuator_mqtt_client_timer.topic)


        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    #notify actuator 
    def notify (self, paho_mqtt , userdata, msg):

        #Read update from MQTT broker
        payload=json.loads(msg.payload)
        self.actuator.state = payload['e'][0]['vb']
        #print(">>>>>>>>>> actuator ",payload)
        
                
    # overridden Thread run method
    def run( self ):
        
        last_time = datetime.utcnow()
        while(True):

            actual_time = datetime.utcnow()

            
            for timestamp in self.timestamp_list:

                aux_time = datetime.strptime(timestamp, "%H:%M:%S")
                aux_time = aux_time.replace(year = actual_time.year, month = actual_time.month, day = actual_time.day)
                print("Triggering time: ",aux_time)
                print("Last time: ",last_time)
                print("Actual time: ",actual_time)
                if((actual_time)>(aux_time) and (last_time)<=(aux_time)):
                    self.actuator.state = True
                    print("Single time control triggered")
                    if(self.actuator_mqtt_client_timer != None):
                        self.actuator_mqtt_client_timer.publish(self.actuator.to_message_actuator())

            last_time = datetime.utcnow()
            #print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            #print(str(self.getName()), "done sleeping")




class Control_thread_timer_interval( threading.Thread):


    def __init__(self, threadName, actuator, measurement_mqtt_client, actuator_mqtt_client, time_interval, sleepTime=5):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.actuator=actuator
        self.measurement_mqtt_client=measurement_mqtt_client
        self.actuator_mqtt_client=actuator_mqtt_client
        self.sleepTime = sleepTime
        self.time_interval = time_interval

        #EDIT: notify modified 
        self.actuator_mqtt_client.client.paho_mqtt.on_message=self.notify1
        self.measurement_mqtt_client.client.paho_mqtt.on_message=self.notify2

        self.actuator_mqtt_client.client.mySubscribe(self.actuator_mqtt_client.topic)
        self.measurement_mqtt_client.client.mySubscribe(self.measurement_mqtt_client.topic)

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    #notify actuator 
    def notify1 (self, paho_mqtt , userdata, msg):

        #Read update from MQTT broker
        payload=json.loads(msg.payload)
        self.actuator.state = payload['e'][0]['vb']
        #print(">>>>>>>>>> actuator ",payload)
    

    #notify sensor
    def notify2 (self, paho_mqtt , userdata, msg):

        #Read update from MQTT broker
        payload=json.loads(msg.payload)
        self.actuator.sensor.measure = payload['e'][0]['v']
        #print(">>>>>>>>>> sensor ",payload)
        
                
    # overridden Thread run method
    def run( self ):
        while(True):
            if(self.time_interval!=[]):
                actual_time = datetime.utcnow()
                time_init = datetime.strptime(self.time_interval[0], "%H:%M:%S")
                time_init = time_init.replace(year = actual_time.year, month = actual_time.month, day = actual_time.day)
                time_end = datetime.strptime(self.time_interval[1], "%H:%M:%S")
                time_end = time_end.replace(year = actual_time.year, month = actual_time.month, day = actual_time.day)
                print(">> considered interval -> ",time_init, " - ", time_end)
                print("Actual time -> ",actual_time)
                if((actual_time)>(time_init) and (actual_time)<=(time_end)):
                    self.actuator.state = True
                    print("Interval time control triggered")
                    if(self.actuator_mqtt_client != None):
                        self.actuator.run_control(self.actuator_mqtt_client)
                        #self.actuator_mqtt_client.publish(self.actuator.to_message_actuator())
                
                #print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
                time.sleep( self.sleepTime )
                #print(str(self.getName()), "done sleeping")
            
