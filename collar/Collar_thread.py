from pythonping import ping
import time
import threading
import requests 


class Pinging_thread( threading.Thread): 


    def __init__(self, threadName, ip_to_ping, deviceManager, base_name, sleepTime=10):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.base_name = base_name
        self.ip_to_ping = ip_to_ping
        self.deviceManager = deviceManager
        self.sleepTime = sleepTime
        self.state = int(False)

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    
    #function to create message with details for publisher 
    def to_message(self):
        
        message = {}
        message['e'] = []
        
        message['bt'] = str(time.time())
        message['bn'] = self.base_name
        message['e'].append({ 'n' : 'collar_'+str(self.ip_to_ping), 'u' : 'bool','t' : str(time.time()), 'v' : self.state})
        
        return message 


                
    # overridden Thread run method
    def run( self ):

        while(True):
            
            #ping 
            res = ping(self.ip_to_ping, count = 1)

            if (res._responses[0].success):

                print(">> FOUND <<")    
                self.state=int(True)

            else:

                print(">> NOT found <<")  
                self.state=int(False )             


            message={"IP" : self.ip_to_ping, "state" : self.state}
            self.deviceManager.publish(self.to_message())
            print(self.to_message())
            print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            print(str(self.getName()), "done sleeping")





class Alive_thread_collar( threading.Thread ):


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

            print('----- NEW_JSON RESPOSE -----')
            print(new_json)
            
            print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            print(str(self.getName()), "done sleeping")






