import time

class simulator:


    def __init__(self, initial_condition=0, loading_rate=0, downloading_rate=0, delta_t=0):

        self.actual_state=initial_condition
        self.loading_rate=loading_rate
        self.downloading_rate=downloading_rate
        self.delta_t=delta_t
        
    
    #function to emulate filling and emptying 
    def run(self, actuator_state):

        if(actuator_state==True):

            self.actual_state=self.actual_state+self.loading_rate*self.delta_t
            
        else:

            self.actual_state=self.actual_state-self.downloading_rate*self.delta_t 
            
            if(self.actual_state<=0):

                self.actual_state=0
                
        print(f">> actual_STATE -> {self.actual_state} <<")
            
        return


if __name__ == '__main__':

    s=simulator(10,1,1,1)

    while(True):
        
        s.run(True)
        time.sleep(s.delta_t)
        
    