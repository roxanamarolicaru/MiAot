import Miaot_catalog_threads  
import json
import sys

if __name__ == '__main__':

	#Global variables
	systems_list = [] #List of the connected devices

	#Load configuration file
	try:
		conf_json = json.load(open(str(sys.argv[1])))
	except:
		#No conf provided end script and threads
		print("No configuration file provided as argument")
		sys.exit()

	#Creation of threads
	thread_rest = Miaot_catalog_threads.RestFULL_thread("REST Thread", conf_json, systems_list)	
	thread_control = Miaot_catalog_threads.Control_thread("Control Thread", systems_list, conf_json["alive_sleeping_time"]) 	
	print("Starting threads")

	#Start threads
	thread_rest.start() # invokes run method of thread1 
	thread_control.start() # invokes run method of thread2 
	
	print("Threads started")
