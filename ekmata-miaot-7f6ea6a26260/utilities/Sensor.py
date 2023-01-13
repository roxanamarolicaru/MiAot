import time

class sensor:


    def __init__(self, id=-1, name=None, unit=None):

        self.id = id
        self.name = name
        self.unit = unit
        self.measure = -1
        self.time = -1
    

    def read_measure(self, value=None):
        
        self.measure = value
        self.time = str(time.time())