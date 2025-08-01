# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.clientLibraries.rpclpy.node import Node
from messages import *
from rpio.clientLibraries.rpclpy.utils import timeit_callback

import time
import yaml

#<!-- cc_include START--!>
import json

#<!-- cc_include END--!>

#<!-- cc_code START--!>
def json_to_object(json_data, cls):
    """
    Fills and returns an instance of `cls` using the JSON data provided.
    
    Args:
        json_data (str or dict): JSON string or parsed dict.
        cls (type): The class to instantiate and fill.
        
    Returns:
        An instance of `cls` with attributes from JSON.
    """
    # Parse JSON if it's a string
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    
    # Extract matching arguments based on class __init__
    try:
        obj = cls(**json_data)
    except TypeError:
        # Fallback: create empty object and manually set attributes
        obj = cls.__new__(cls)
        for key, value in json_data.items():
            setattr(obj, key, value)
        if hasattr(obj, '__init__'):
            try:
                obj.__init__()
            except TypeError:
                pass  # if __init__ expects parameters we skip calling it
    return obj
#<!-- cc_code END--!>

class Monitor(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Monitor"
        self.logger.info("Monitor instantiated")

        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR monitor_data-----------------------------
    @timeit_callback
    def monitor_data(self,msg):
        _LaserScan = LaserScan()

        #<!-- cc_code_monitor_data START--!>

        # user code here for monitor_data

        _laser_scan = json_to_object(msg, LaserScan)
        json_message = json.loads(msg)
        _laser_scan._ranges = json_message['ranges']

        #<!-- cc_code_monitor_data END--!>

        # _success = self.knowledge.write(cls=_LaserScan)
        self.write_knowledge("laser_scan",msg)
        #use the bellew
        self.write_knowledge(_laser_scan)
        
        self.publish_event(NewData)

    def register_callbacks(self):
        self.register_event_callback(event_key='/Scan', callback=self.monitor_data)     # LINK <eventTrigger> Scan

def main(args=None):
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except:
        raise Exception("Config file not found")
    
    node = Monitor(config=config)
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()