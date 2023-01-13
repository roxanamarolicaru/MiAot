import json
import datetime
import cherrypy
import copy

# Class for identifying each system (home systems)
class Miaot_system:
    
     def __init__(self, System_id = -1):
         self.system_id = System_id
         self.id_counter = 0
         self.device_list = [] 

#function to convert from timestamp to string "yyyy-mm-dd"
def myconverter(obj):

    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    

class MiAot_catalog(object): 


    exposed=True
    
    #Attributes
    def __init__ (self, conf_json, systems_list):

        self.systems_list = systems_list
        self.json_answer_init = {
              "message_broker": conf_json["mqtt_message_broker"],
              "message_broker_port": conf_json["mqtt_port"],
              "assigned_id" : -1,
              "device_list": []
        }
        self.json_answer = {}
        self.id_counter=0

        return
    

    #GET method
    def GET(self,*uri, **params):  

        self.json_answer = copy.copy(self.json_answer_init)
        
        try:
            #Get system id from parameters
            system_id = cherrypy.request.params.get("system_id")
            
            #Look for that system_id in the systems list
            system_found = next((x for x in self.systems_list if int(x.system_id) == int(system_id)), None)
            
            if (system_found != None):
                
                #Generate output
                self.json_answer['device_list'] = system_found.device_list
                self.json_answer['assigned_id'] = system_found.id_counter
                y = json.dumps(self.json_answer, default = myconverter)
            else:
                print("System not found")
                self.json_answer = copy.copy(self.json_answer_init)   
                y = json.dumps(self.json_answer, default = myconverter)
        
        except:
            self.json_answer = copy.copy(self.json_answer_init)
            y = json.dumps(self.json_answer, default = myconverter)
            
        return str(y)
    
    #POST method
    def POST (self, *uri, **params):
        
        self.json_answer = copy.copy(self.json_answer_init) 
        
        #Get the body from the request
        body =cherrypy.request.body.read()
        obj = json.loads(body)
        
        #Get system id
        system_id = obj.pop("system_id")
        
        #Set timestamp for the first registration
        obj['timestamp'] = datetime.datetime.utcnow() #Decide if the date must be kept
        
        #Look for that system_id in the systems list
        system_found = next((x for x in self.systems_list if int(x.system_id) == int(system_id)), None)
                            
        #Create not existing system
        if(system_found == None):
            system_found = Miaot_system(int(system_id))
            self.systems_list.append(system_found)
            
            
        system_found.device_list.append(obj)
        system_found.id_counter += 1
        assigned_id = system_found.id_counter
            
        obj["id"] = assigned_id
        
        #Generate output
        self.json_answer['device_list'] = system_found.device_list
        self.json_answer["assigned_id"] = assigned_id

        y = json.dumps(self.json_answer, default = myconverter)

        return str(y)
        
    #PUT method
    def PUT (self, *uri, **params): 
        
        self.json_answer = copy.copy(self.json_answer_init)
        
        #Get the body from the request
        body =cherrypy.request.body.read()
        obj = json.loads(body)
        
        #Get system id
        system_id = obj.pop("system_id")
        
        #Look for that system_id in the systems list
        system_found = next((x for x in self.systems_list if int(x.system_id) == int(system_id)), None)
        
        if (system_found != None):
            
            #Searh on device_list for the input id and update timestamp
            json_found =  next((x for x in system_found.device_list if int(x['id']) == int(obj['id'])), None)
           
            if(json_found != None):
                
                json_found['timestamp'] = datetime.datetime.utcnow()
    
            else:
    
                print(">> Device not found <<")
                
            #Generate output
            self.json_answer['device_list'] = system_found.device_list
            y = json.dumps(self.json_answer, default = myconverter)
        
        else:
            y = "System not found"
            print(">> System not found <<")
            
        return str(y)


