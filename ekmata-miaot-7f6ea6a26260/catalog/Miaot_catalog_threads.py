import threading
import random
import cherrypy
import Miaot_catalog 
import time
import datetime


#REST Thread
class RestFULL_thread( threading.Thread ):
    

    def __init__(self, threadName, json_conf, systems_list):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.sleepTime = random.randrange(1,6)
        self.json_conf = json_conf
        self.systems_list=systems_list

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    # overridden Thread run method
    def run( self ):

        #Standard configuration to serve the url "localhost:8080" 
        conf={
            '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(), 
                'tool.session.on':True,
            }
        }
        cherrypy.tree.mount(Miaot_catalog.MiAot_catalog(self.json_conf, self.systems_list),'/',conf)
        cherrypy.server.socket_host = self.json_conf["catalog_ip"]
        cherrypy.engine.start()
        cherrypy.engine.block()
        


# Control thread for disconnected devices
class Control_thread( threading.Thread ): 

    def __init__(self, threadName, systems_list, sleepTime=5, controlAliveTime=30):

        #Initialize thread, set sleep time, print data
        threading.Thread.__init__(self, name=threadName)
        self.sleepTime = sleepTime
        self.systems_list=systems_list
        self.controlAliveTime=controlAliveTime

        print("Name:",  str(self.getName()), "sleep: " ,self.sleepTime)


    # overridden Thread run method
    def run( self ):

        while(True):

            #Sleep for 1-5 seconds
            #Search on device_list for the input id and update timestamp
            
            #Get the actual time
            actual_time = datetime.datetime.utcnow()
            
            #Control if a device didn't report itself
            for i, system_aux in enumerate(self.systems_list):
                for j, device_aux in enumerate(system_aux.device_list):
                    if((actual_time - device_aux['timestamp']).total_seconds() >= self.controlAliveTime):
                        print("Device = ",device_aux["id"]," was disconnected")
                        system_aux.device_list.remove(device_aux)
                    
            print(str(self.getName()), "going to sleep for",self.sleepTime,"second(s)")
            time.sleep( self.sleepTime )
            print(str(self.getName()), "done sleeping")
        