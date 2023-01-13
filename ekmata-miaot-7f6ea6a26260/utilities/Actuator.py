import time 

class actuator:


    def __init__(self, id=-1, base_name=None, name=None, sensor=None, threshold_min=None, threshold_max=None):
        
        self.id = id
        self.base_name = base_name
        self.name = name
        self.sensor = sensor
        self.state = False
        self.time = str(time.time())

        #EDIT: substitution "none" with "-inf" for computation
        if (threshold_min == "None"):
            self.threshold_min = float("-inf")
        else:
            self.threshold_min = threshold_min
        #EDIT: substitution "none" with "inf" for computation
        if (threshold_max == "None"):
            self.threshold_max = float("inf")
        else:
            self.threshold_max = threshold_max



    #function to manage the actuator using thresholds 
    def run_control(self, actuatorPublisher = None):
        
        if (self.sensor != None):
            print("Actual sensor measure = ", self.sensor.measure)
            if(self.threshold_min != None and self.sensor.measure < self.threshold_min):
                print("threshold_min = ", self.threshold_min)
                self.state = True
                if(actuatorPublisher != None):
                    actuatorPublisher.publish(self.to_message_actuator())
            if(self.threshold_max != None and self.sensor.measure > self.threshold_max):
                print("threshold_max = ", self.threshold_max)
                self.state = False
                if(actuatorPublisher != None):
                    actuatorPublisher.publish(self.to_message_actuator())
        self.time=str(time.time())
    

    #function to create message with details for publisher - sensor 
    def to_message_sensor(self):
        message = {}
        message['bt'] = str(time.time())
        message['bn'] = self.base_name
        message['e']=[{ 'n' : self.sensor.name, 'u' : self.sensor.unit,'t' : self.sensor.time, 'v' : self.sensor.measure}]
        return message 


    #function to create message with details for publisher - actuator 
    def to_message_actuator(self):
        message = {} 
        message['bt'] = str(time.time())
        message['bn'] = self.base_name
        message['e']=[{'n' : self.name, 'vb' : self.state, 't' : self.time}]
        return message 
    

    #function used by the device to update the actuator from mqtt
    def callback_actuator(self, message):
        self.state = message['e'][0]['vb']
        return
